#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import xmltodict
import sys
import re
from datetime import datetime

def convert_data(in_data):
    result=[]
    index=0
    for key in in_data["receipts"]:
        dst={}
        src = in_data["receipts"][key]
        if src["subtype"]!="receipt":
            print("непонятный тип записи - выход")
            print(json.dumps(src, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
            # для пропуска:
            #continue
            sys.exit(1)

        # кривой id:
        if type(src["id"]) is dict:
            print("id is dict!")
            if "$oid1" in src["id"]:
                dst["_id"]=src["id"]["$oid"]
            else:
                print("неизвестный тип идентификатора:")
                print(json.dumps(src["id"], sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
                sys.exit(1)
        else:
            dst["_id"]=src["id"]
        del src["id"]

        # кривая дата:
        if type(src["receiveDate"]) is dict:
            print("receiveDate is dict!")
            if "$date" in src["receiveDate"]:
                # нужно сконвертировать в текстовую дату:
                timestamp=src["receiveDate"]["$date"]/1000
                dst["createdAt"]=datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
            else:
                print("неизвестный тип идентификатора:")
                print(json.dumps(src["receiveDate"], sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
                sys.exit(1)
        else:
            dst["createdAt"]=src["receiveDate"]
        del src["receiveDate"]

        # кривая дата внутри данных:
        if type(src["content"]["dateTime"]) is dict:
            print("dateTime is dict!")
            if "$date" in src["content"]["dateTime"]:
                # нужно сконвертировать в текстовую дату:
                timestamp=src["content"]["dateTime"]["$date"]/1000
                del src["content"]["dateTime"]
                src["content"]["dateTime"]=datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
            else:
                print("неизвестный тип идентификатора:")
                print(json.dumps(src["content"]["dateTime"], sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
                sys.exit(1)

        dst["ticket"]={}
        dst["ticket"]["document"]={}
        if "rawData" in src["content"]:
            del src["content"]["rawData"]
        if "retailPlaceAddress" not in src["content"] and "address" in src:
            src["content"]["retailPlaceAddress"]=src["address"]

        dst["ticket"]["document"]["receipt"]=src["content"]
        result.append(dst)
        index+=1

        #if index > 9: 
            #print(json.dumps(src, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
         #   break
    print("сконвертировал %d записей"%index)
    return result

if len(sys.argv) < 3:
	print("Необходимо два параметра: имя входного файла, имя выходного файла")
	print("Выход")
	raise SystemExit(1)

#print(sys.argv)

print("load source from file: %s"%sys.argv[1])
f=open(sys.argv[1],"r")
in_data = json.loads(f.read())
#print(json.dumps(in_data, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
out_data=convert_data(in_data)
#print(out_data)

print("save to file: %s"%sys.argv[2])
f = open(sys.argv[2], mode="w+", encoding="utf-8")
f.write(json.dumps(out_data, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
f.close()

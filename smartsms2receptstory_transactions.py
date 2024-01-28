#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import os
import traceback
import sys
import re
from datetime import datetime

def get_exception_traceback_descr(e):
  if hasattr(e, '__traceback__'):
    tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
    result=""
    for msg in tb_str:
      result+=msg
    return result
  else:
    return e

def fill_def(src,index):
    try:
        uniq_number=-1000000-index
        result={}
        result["document"]={}
        result["document"]["receipt"]={}
        totalsum=int(abs(src["transactionAmount"]*100))
        dst=result["document"]["receipt"]
        dst["buyerAddress"]=""
        dst["cashTotalSum"]=totalsum
        dst["dateTime"]=src["date"]
        dst["ecashTotalSum"]=0
        dst["fiscalDocumentNumber"]=uniq_number
        dst["fiscalDriveNumber"]=0
        dst["fiscalSign"]=uniq_number
        dst["kktRegId"]=0
        dst["nds10"]=0
        dst["nds18"]=0
        dst["ndsNo"]=0
        dst["operationType"]=1
        dst["rawData"]=""
        dst["receiptCode"]=0
        dst["requestNumber"]=0
        dst["shiftNumber"]=0
        dst["taxationType"]=0
        dst["totalSum"]=totalsum
        dst["user"]=""
        #dst["userInn"]="2dfc02f16"
        dst["items"]=[]
        item={}
        if "note" in src and src["note"]!="":
            item["name"]=src["note"]
        else:
            item["name"]="неопределённые работы"
        item["nds10"]=0
        item["nds18"]=0
        item["ndsNo"]=0
        item["price"]=totalsum
        item["quantity"]=1
        item["sum"]=item["price"]*item["quantity"]
        dst["items"].append(item)
        return result
    except Exception as e:
        print(get_exception_traceback_descr(e))
        print("error with item:")
        print(json.dumps(src, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
        return None

def bank(src,index):
    try:
        result = fill_def(src,index)
        if result is None:
            print("error with item:")
            print(json.dumps(src, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
            return None
        result["document"]["receipt"]["items"][0]["name"]="Оплата кредита"
        result["document"]["receipt"]["userInn"]="375ab372d"
        return result
    except Exception as e:
        print(get_exception_traceback_descr(e))
        print("error with item:")
        print(json.dumps(src, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
        return None

def stroika(src,index):
    try:
        result = fill_def(src,index)
        if result is None:
            print("error with item:")
            print(json.dumps(src, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
            return None
        result["document"]["receipt"]["userInn"]="2dfc02f16"
        return result
    except Exception as e:
        print(get_exception_traceback_descr(e))
        print("error with item:")
        print(json.dumps(src, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
        return None

def nalichnie(src,index):
    result={}
    try:
        if "subcategory" in src and (src["subcategory"]=="Капремонт" or src["subcategory"]=="Стройка и ремонт"):
            result = stroika(src,index)
        return result
    except Exception as e:
        print(get_exception_traceback_descr(e))
        print("error with item:")
        print(json.dumps(src, sort_keys=True,indent=4, separators=(',', ': '),ensure_ascii=False))
        return None

def convert_data(in_data):
    result=[]
    index=0
    transaction_id=0
    for src in in_data["operations"]:
        transaction_id+=1
        dst={}
        # наличка:
        if src["operationType"]=="CASH_TRANSACTION": # and src["operationKind"]=="TRANSFER_OUT":
            ret=nalichnie(src,transaction_id)
            if ret is not None and ret !={}:
                index+=1
                result.append(ret)
        # Кредит:
        if src["operationType"]=="ACCOUNT_TRANSACTION" and src["operationKind"]=="TRANSFER_OUT" and \
                src["category"]=="Банк" and src["subcategory"]=="Кредит" and src["affectStatistics"]==False and \
                (("tags" in src and not ("На закрытие кредита" in src["tags"] and "Витя" in src["tags"])) or \
                "tags" not in src):
            ret=bank(src,transaction_id)
            if ret is not None and ret !={}:
                index+=1
                result.append(ret)

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

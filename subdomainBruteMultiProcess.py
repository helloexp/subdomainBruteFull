#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 获取指定域名的dns记录，找到域名的所有子域名  优化版本：采用多进行执行
# version v1.0

from dns import resolver
from itertools import permutations
from pandas import DataFrame
from multiprocessing import Pool
import time,os,dns


def getDNS(processName,clist):
	print("Run task {}:{}".format(processName,os.getpid()))
	start=time.time()

	my_resolver=resolver.Resolver()
	my_resolver.nameservers=['114.114.114.114']

	queryType=['A','AAAA','CNAME','NS','MX','TXT','PTR']
	answerDic={}
	answers=[]
	questions=[]

	for x in clist:
		try:
			name=x+".baidu.com"
			print('pid ',os.getpid(),' querying ',name)
			ans=my_resolver.query(name)
			
			indexQuestion=str(ans.response).index(';QUESTION')+10
			indexAnswer=str(ans.response).index(';ANSWER')-1
			indexAuthority=str(ans.response).index(';AUTHORITY')-1

			question=(str(ans.response)[indexQuestion:indexAnswer])

			indexAnswer=indexAnswer+9
			answer=(str(ans.response)[indexAnswer:indexAuthority]).replace('\n','---')

			answerDic[question]=answer	
		except Exception as e:
			print('     ',e)
			pass		

	questions.extend(answerDic.keys())
	answers.extend(answerDic.values())
	print(str(os.getpid()),' process answerDic\'s length is :',len(answerDic))

	ansDic=list(zip(questions,answers))

	df=DataFrame(data=ansDic,columns=['查询的域名','查询结果'])
	df.to_csv('./out/'+str(os.getpid())+'dns.csv',encoding='utf-8-sig')

	end=time.time()
	print("Task {} runs {} seconds".format(processName,end-start))

	return ansDic
		

def getRandom(num):
	returnList=[]
	#chars='abcdefghijklmnopqrstuvwxyz1234567890'	
	chars='abcdefghijklmnopqrstuvwxyz'
	clist=list(permutations(chars,num))
	if num>1:
		for x in chars:
			clist.append(str(x)*num)
			pass
	
	for i in clist:
		returnList.append("".join(i))
	pass
	print('total query num:',len(returnList))
	return returnList


if __name__ == '__main__':
	processNum=6
	print("Parent process {}".format(os.getpid()))
	p=Pool(processNum+1)

	clist=getRandom(2)
	eachList=len(clist)//processNum
	print('每个进程处理的数量：',eachList)
	
	start=time.time()
	for i in range(processNum+1):
		iList=clist[i*eachList:eachList*(i+1)+1]
		# print(len(i),' ',)	
		p.apply_async(getDNS,args=(i,iList))



	print("Waiting for all subprocess done...")
	p.close()
	p.join()
	print("All subprocess done！！！")
	stop=time.time()
	print("总计花费时间：",stop-start)
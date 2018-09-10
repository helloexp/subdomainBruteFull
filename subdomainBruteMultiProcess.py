#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 获取指定域名的dns记录，找到域名的所有子域名  优化版本：采用多进行执行
# version v1.1.1

from dns import resolver
from itertools import permutations
from pandas import DataFrame
from multiprocessing import Pool
import time,os,dns,sys,getopt


def getDNS(processName,clist,domainName,outDir):
	print("Run task {}:{}".format(processName,os.getpid()))
	start=time.time()

	# 支持自定义dns服务器
	# my_resolver=resolver.Resolver()
	# my_resolver.nameservers=['114.114.114.114']

	my_resolver=resolver

	queryType=['A','AAAA','CNAME','NS','MX','TXT','PTR']
	answerDic={}
	answers=[]
	questions=[]

	count=0

	for x in clist:
		count+=1
		try:
			name=x+"."+domainName
			line=count//1000
			if count%1000==0:
				print(line,'->','pid ',os.getpid(),' querying ',name)
			ans=my_resolver.query(name)
			
			indexQuestion=str(ans.response).index(';QUESTION')+10
			indexAnswer=str(ans.response).index(';ANSWER')-1
			indexAuthority=str(ans.response).index(';AUTHORITY')-1

			question=(str(ans.response)[indexQuestion:indexAnswer])

			indexAnswer=indexAnswer+9
			answer=(str(ans.response)[indexAnswer:indexAuthority]).replace('\n','---')

			answerDic[question]=answer	
		except Exception as e:
			#print('     ',e)
			pass		

	questions.extend(answerDic.keys())
	answers.extend(answerDic.values())
	print(str(os.getpid()),' process answerDic\'s length is :',len(answerDic))

	ansDic=list(zip(questions,answers))

	df=DataFrame(data=ansDic,columns=['查询的域名','查询结果'])
	df.to_csv('./{}/'.format(outDir)+str(os.getpid())+'dns.csv',encoding='utf-8-sig')

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

	if os.name=='nt':
		os.system('cls')
	else:
		os.system('clear')


	alphaNum=2

	opts,args=getopt.getopt(sys.argv[1:],'hd:o:n:')

	usage="""

		subdomainBruteMultiProcess  version 1.1.1

		DABIAOGE  


	-d    指定要查询的域名
	-o    指定要输出结果的目录
	-n    设置子域名的字母数，默认为2
	-h    输出此帮助

	eg:   python subdomainBruteMultiProcess.py -d baidu.com -o baidu -n 2

			"""

	for opt,value in opts:
		if opt=='-d':
			if len(value)==0:
				print(usage)
				sys.exit(0)
			else:
				domainName=value

		elif opt=='-o':
			if len(value)==0:
				print(usage)
				sys.exit(0)
			else:
				outDir=value
		elif opt=='-n':
			if len(value)==0:
				print(usage)
				sys.exit(0)
			else:
				alphaNum=int(value)
		elif opt=='-h':
			print(usage)
			sys.exit(0)

	msg='您要查询的域名：{}，查询的子域名字母数：{}，输出目录：{}'.format(domainName,alphaNum,outDir)
	print(msg)
	sys.exit(0)	
	
	processNum=35
	if alphaNum==1:
		processNum=1

	if os.path.exists(outDir):
		print('out path exists')
	else:
		os.mkdir(outDir)
		print('out path not exists',' 创建out文件夹成功')
		
	print("Parent process {}".format(os.getpid()))
	p=Pool(processNum+1)

	clist=getRandom(alphaNum)
	eachList=len(clist)//processNum
	print('每个进程处理的数量：',eachList)
	
	start=time.time()
	for i in range(processNum+1):
		iList=clist[i*eachList:eachList*(i+1)+1]		
		p.apply_async(getDNS,args=(i,iList,domainName,outDir))


	print("Waiting for all subprocess done...")
	p.close()
	p.join()
	print("All subprocess done！！！")
	stop=time.time()
	print("总计花费时间：",stop-start)
	runtime=open('./{}/time.txt'.format(outDir),'w')
	runtime.write('总计花费时间：'+str(stop-start)+' s')
	runtime.close
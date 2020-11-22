import pandas as pd
import random
import argparse
from operator import itemgetter 
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--input',help='enter the input')
parser.add_argument('--output',help="enter the output location")
args=parser.parse_args()
#print(args)	
if args.input==None or args.output==None:
	print("wrongs args")
	exit()

#movies = pd.read_csv("movies.csv",encoding="Latin1")
Ratings = pd.read_csv("ratings.csv")

def getmatrix(Ratings):

	fin=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')

	#print(final)
	final=fin.fillna(final.mean(axis=0))
	#print(final)
	corr=final.transpose()
	corr_final=corr.corr(method='pearson')
	return fin,final,corr_final
	
def top(user,corr):
	res=corr.iloc[user-1]
#	print(res)
	final_res=dict()
	for x in range(len(res)):
		final_res[res.iloc[x]]=x+1
	res=sorted(list(res),reverse=True)
	re=[]
	for x in range(len(res)):
		if(final_res[res[x]]!=user):
			re.append((final_res[res[x]],res[x]))
	return re
	
	


def calculate_rating(final,res,user,movie):
	corr_sum=0
	pi_pm=0
	movie=movie
	user=user
	x=0
	y=0
	while y<15 and x<len(res):
		if res[x][0] in final.index:
			if not np.isnan(final.loc[res[x][0],movie]):
				corr_sum+=res[x][1]
				#t = final.loc[final_res[res_[x]],movie] - temp.mean(axis=0)
				t = final.loc[res[x][0],movie]*res[x][1]
				pi_pm+=t
				t=0
				y=y+1
		x=x+1

	mu_rating = final.loc[user]
	mu_rating = mu_rating.mean(axis=0)

	grand_rating =  (pi_pm/corr_sum)
	return grand_rating

g=[]
def evaluate(final_matrix,corr_matrix,userID,movieID):
	set=False
	usertop_n=None
	for i in g:
		if i[0]==userID:
#			print("exists "+str(userID))
			set=True
			usertop_n=i[1]
			break
	if set==False:
		usertop_n=top(userID,corr_matrix)
		g.append((userID,usertop_n))
	res_final=calculate_rating(final_matrix,usertop_n,userID,movieID)
	return res_final
	
def process(userlist,ratings):
	fin,final,corr=getmatrix(ratings)
#	print(fin)
#	fin.to_csv("a.csv")
	for i in userlist:	
		mov={}
		seen=set()
#		print(fin)
#		print(fin.loc[int(i),:])
		us=fin.loc[int(i),:].notna()
#		print(us)
		for x in fin.columns:
			if us[x]==True:
				seen.add(x)
#		print(us.index)
#		print(len(seen))
		#print(seen)
		for j in final.columns:
			if j not in seen:
		  		re=evaluate(final,corr,int(i),j)
		  		mov[j]=re
		res = dict(sorted(mov.items(), key = itemgetter(1), reverse = True)[:5])
		print(res)
		use=fin.loc[int(i),:]
		print(use.nlargest())
	  	
	   	
	  
file1 = open(args.input, 'r') 
Lines = file1.readlines()
process(Lines,Ratings)

import pandas as pd
import random
import argparse
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
Ratings = pd.read_csv(args.input)

def getmatrix(Ratings):

	final=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')

	#print(final)
	final=final.fillna(final.mean(axis=0))
	#print(final)
	corr=final.transpose()
	corr_final=corr.corr(method='pearson')
	return final,corr_final
	
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
	a=True
	x=0
	y=0
	while a==True:
		if y<15 and x<len(res):		
			if np.isnan(final.loc[res[x][0],movie]):
				x=x+1
			else:
				corr_sum+=res[x][1]
				#t = final.loc[final_res[res_[x]],movie] - temp.mean(axis=0)
				t = final.loc[res[x][0],movie]*res[x][1]
				pi_pm+=t
				t=0
				y=y+1
				x=x+1
		else:
			a=False

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
    
def genfolds(Ratings):
#	print(len(Ratings))
	chunk=len(Ratings)//5
	folds=[]
	indexes=list(Ratings.index.values)
	overall=set()
	for i in range(4):
		testchunk=set()
		while(len(testchunk)!=chunk):
			val=random.randint(0,len(indexes)-1)
			if indexes[val] not in overall:
				testchunk.add(indexes[val])
				overall.add(indexes[val])
		testchunk=list(testchunk)
		testratings=Ratings.iloc[testchunk]
		folds.append(testratings)
	trainratings=Ratings.drop(overall,axis=0)
	folds.append(trainratings)
#	print(testratings)
#	print(trainratings)
	#print(testchunk)
#	print(folds)
	return folds

def MAE():
	folds=genfolds(Ratings)
	overall=0	
	ocount=0
	for i in range(5):
		test=folds[i]
		train=Ratings.drop(list(test.index.values),axis=0)
		train_fr,corr=getmatrix(train)
#		print(train)
#		print(train_fr)
#		print(corr)
		
		mae_sum=0
		count=0
		
		for val in list(test.index.values):
			if test.loc[val,'userId'] in corr.index and test.loc[val,'movieId'] in train_fr.columns:
					#print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Actual Rating: "+str(test.loc[val,'rating']))
					re=evaluate(train_fr,corr,int(test.loc[val,'userId']),int(test.loc[val,'movieId']))
					#print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Predicted Rating: "+str(re))
					mae_sum+=abs(test.loc[val,'rating'] - re)
					count+=1
		print("After one iteration without changing Top_N Mean absolute Error :"+str(mae_sum/count))
		overall+=mae_sum
		ocount+=count
	print("Overall without changing Top_N Mean absolute Error :"+str(overall/ocount))
	
#userid_dict,userTop_n=Top_N(52,64620,corr_final)
#print(calculate_rating(final,userid_dict,userTop_n,52,64620))
#print(evaluate(final,corr_final,1,1208))
#print("working",end=" ",flush=True)
MAE()
#f,corr=getmatrix(Ratings)
#print(Ratings)
#print(Ratings.iloc[0])
#x=top(1,corr)
#print(x)
#print(calculate_rating(f,x,1,1))

	

import pandas as pd
import random
import argparse
import numpy as np
import itertools
import csv

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

	fin=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')

	#print(final)
	final=fin.fillna(fin.mean(axis=0))
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
	
	


def calculate_rating(fin,final,res,user,movie):
	corr_sum=0
	pi_pm=0
	movie=movie
	user=user
	x=0
	y=0
	while y<15 and x<len(res):
		if res[x][0] in final.index:
			if not np.isnan(fin.loc[res[x][0],movie]):
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
def evaluate(fin,final_matrix,corr_matrix,userID,movieID):
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
	res_final=calculate_rating(fin,final_matrix,usertop_n,userID,movieID)
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
    d_er={}
    d_oer={}
    folds=genfolds(Ratings)
    overall=0
    ocount=0
    for i in range(5):
        test=folds[i]
        train=Ratings.drop(list(test.index.values),axis=0)
        fin,train_fr,corr=getmatrix(train)
#		print(train)
#		print(train_fr)
#		print(corr)
		
        mae_sum=0
        count=0
		
        for val in list(test.index.values):
            if test.loc[val,'userId'] in corr.index and test.loc[val,'movieId'] in train_fr.columns:
                    #print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Actual Rating: "+str(test.loc[val,'rating']))
                    re=evaluate(fin,train_fr,corr,int(test.loc[val,'userId']),int(test.loc[val,'movieId']))
                    if re>5:
                            re=5
                    #print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Predicted Rating: "+str(re))
                    mae_sum+=abs(test.loc[val,'rating'] - re)
                    count+=1
        print("After one iteration without changing Top_N Mean absolute Error :"+str(mae_sum/count))
        overall+=mae_sum
        ocount+=count
        d_er.update({i+1 : mae_sum/count})
    print("Overall without changing Top_N Mean absolute Error :"+str(overall/ocount))
    d_oer.update({"average": overall/ocount})
    return d_er,d_oer
	
#userid_dict,userTop_n=Top_N(52,64620,corr_final)
#print(calculate_rating(final,userid_dict,userTop_n,52,64620))
#print(evaluate(final,corr_final,1,1208))
#print("working",end=" ",flush=True)
er,oer=MAE()
#f,corr=getmatrix(Ratings)
#print(Ratings)
#print(Ratings.iloc[0])
#x=top(1,corr)
#print(x)
#print(calculate_rating(f,x,1,1))
fields = ['No. of Fold', 'MAE'] 
mydict =[]
app={'No. of Fold':0,'MAE':0}
app2={'No. of Fold':'x','MAE':0}
for j in er:
    app={'No. of Fold': j,'MAE':er[j]}
    mydict.append(app)
#print(mydict)
for j in oer:
    app2={'No. of Fold': j,'MAE':oer[j]}
    mydict.append(app2)
filename = "eval.csv"
  
# writing to csv file 
with open(filename, 'w') as csvfile: 
    # creating a csv dict writer object 
    writer = csv.DictWriter(csvfile, fieldnames = fields) 
      
    # writing headers (field names) 
    writer.writeheader() 
      
    # writing data rows 
    writer.writerows(mydict) 
# process(Lines,Ratings)
	

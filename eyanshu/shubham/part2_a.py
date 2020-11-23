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
Ratings = pd.read_csv(args.input,nrows=40000)
read_rating = pd.read_csv('movies.csv')




genre=set()
for x in range(9742):
    val=read_rating.iloc[x,2]
    val=val.split("|")
#    print(val)
    [genre.add(y) for y in val]

genre_mov=dict()
id_list=[]
genre_mov[""]=[]

ratmat=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
for g in genre:
    genre_mov[g]=[]
    
for x in range(9742):
    id_ = read_rating.iloc[x,0]
    val=read_rating.iloc[x,2]
    val=val.split("|")
    #print(val)
    for v in val:
        l_val=genre_mov[v]
        l_val.append(id_)
        genre_mov[v]=l_val
       
       
def find_genre(id_):
	all_genre=[]
	for x in genre:
		if id_ in genre_mov[x]:
			all_genre.append(x)
	return all_genre   
	 
def genre_corelation(genre,df):
	genrecorr={}
#	print(df)
	df_trans=df.transpose()
#	print(df_trans.loc[6849])
#	print(df_trans)
	for x in genre:
#		print(x)
		#print(genre_mov[x])
		y=[]
		for a in genre_mov[x]:
			if a in df_trans.index:
				y.append(a)
		children=df_trans.loc[y]
		final_children=children.dropna(axis=1,how="all")
		genrecorr[x]=final_children
	return genrecorr
	
def getmatrix(ratings):
	final=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
#	print(final.loc[:,1])
	Ratmat=final
	y=genre_corelation(genre,final)
	fi={}
	for x in y:
		

	#print(final)
		z=y[x].fillna(y[x].mean(axis=0))
	#print(final)
		corr=z.transpose()
		corr_final=corr.corr(method='pearson')
		fi[x]=[y[x],corr_final]
	return fi
  
def top(user,corr):
	res=corr.loc[user]
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
#	print(res)
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
	
	return pi_pm,corr_sum

g=[]
def evaluate(tr,userID,movieID):
	set=False
	usertop_n=None
	genres=find_genre(movieID)
	ta=0
	tb=0
	for gen in genres:
		if userID in tr[gen][1].index and movieID in tr[gen][0].columns:
			for i in g:
				if i[0]==gen and i[1][0]==userID:
		#			print("exists "+str(userID))
					set=True
					usertop_n=i[1][1]
					break
			if set==False:
				usertop_n=top(userID,tr[gen][1])
				g.append((gen,(userID,usertop_n)))
			a,b=calculate_rating(tr[gen][0],usertop_n,userID,movieID)
			ta+=a
			tb+=b
	if tb==0:
		mean=ratmat.mean(axis=1)
		mmean=ratmat.mean(axis=0)
		ome=mean.mean()
		return mmean[movieID]+(mean[userID]-ome)
	return ta/tb
    
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
		tr=getmatrix(train)
#		print(train)
#		print(train_fr)
#		print(corr)
		
		mae_sum=0
		count=0
		
		for val in list(test.index.values):
#			print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Actual Rating: "+str(test.loc[val,'rating']))
			re=evaluate(tr,int(test.loc[val,'userId']),int(test.loc[val,'movieId']))
#			print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Predicted Rating: "+str(re))
			if re!=-1:
				mae_sum+=abs(test.loc[val,'rating'] - re)
				count+=1
		print("After one iteration without changing Top_N Mean absolute Error :"+str(mae_sum/count))
		overall+=mae_sum
		ocount+=count
	d_er.update({i+1 : mae_sum/count})
	print("Overall without changing Top_N Mean absolute Error :"+str(overall/ocount))
	d_oer.update({"total": overall/ocount})
	return d_er,d_oer
#tr=getmatrix(Ratings)
#print(tr)
#x=evaluate(tr,1,47)
#print(x)
er,oer=MAE()
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
filename = "eval2.csv"
  
# writing to csv file 
with open(filename, 'w') as csvfile: 
    # creating a csv dict writer object 
    writer = csv.DictWriter(csvfile, fieldnames = fields) 
      
    # writing headers (field names) 
    writer.writeheader() 
      
    # writing data rows 
    writer.writerows(mydict) 
# process(Lines,Ratings)
	


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
	for x in genre:
		df_trans=df.transpose()
		print(df_trans)
		print(x)
		print(genre_mov[x])
		children=df_trans.loc[genre_mov[x]]
		final_children=children.dropna(axis=1,how="all")
		genrecorr[x]=final_children
	return genrecorr
	
def getmatrix(ratings):
	final=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
	y=genre_corelation(genre,final)
	fi={}
	for x in y:
		

	#print(final)
		y=y.fillna(final.mean(axis=0))
	#print(final)
		corr=y.transpose()
		corr_final=corr.corr(method='pearson')
		fi[x]=(y,corr_final)
	return fi
  
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
			if final.loc[res[x][0],movie]==np.nan:
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
			
	
	return pi_pm,corr_sum

g={}
def evaluate(tr,userID,movieID):
	set=False
	usertop_n=None
	genres=find_genre(movieID)
	ta=0
	tb=0
	for gen in genres:
		for i in g:
			if i[0]==gen and i[1][0]==userID:
	#			print("exists "+str(userID))
				set=True
				usertop_n=i[1][1]
				break
		if set==False:
			usertop_n=top(userID,tr[gen][1])
			g=(gen,(userID,usertop_n))
		a,b=calculate_rating(tr[gen][0],usertop_n,userID,movieID)
		ta+=a
		tb+=b
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
			if test.loc[val,'userId'] in corr.index and test.loc[val,'movieId'] in train_fr.columns:
					#print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Actual Rating: "+str(test.loc[val,'rating']))
					re=evaluate(tr,int(test.loc[val,'userId']),int(test.loc[val,'movieId']))
					#print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Predicted Rating: "+str(re))
					mae_sum+=abs(test.loc[val,'rating'] - re)
					count+=1
		print("After one iteration without changing Top_N Mean absolute Error :"+str(mae_sum/count))
		overall+=mae_sum
		ocount+=count
	print("Overall without changing Top_N Mean absolute Error :"+str(overall/ocount))
tr=getmatrix(Ratings)
print(tr)
x=evaluate(tr,1,1)
print(x)

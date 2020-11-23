import pandas as pd
import random
import argparse
import numpy as np
import itertools
import csv


#Argument handling
parser = argparse.ArgumentParser()
parser.add_argument('--input',help='enter the input')
parser.add_argument('--output',help="enter the output location")
args=parser.parse_args()
if args.input==None or args.output==None:
	print("wrongs args")
	exit()

Ratings = pd.read_csv(args.input,nrows=40000)
read_rating = pd.read_csv('movies.csv')



#this matrix is required to handle case aplification parameters
um_withnan=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
um_i=((um_withnan*0)+1)
um_c=um_i.fillna(0)


#find all genres
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

#genreate utilty matrix according tot the genres   
for x in range(9742):
    id_ = read_rating.iloc[x,0]
    val=read_rating.iloc[x,2]
    val=val.split("|")
    for v in val:
        l_val=genre_mov[v]
        l_val.append(id_)
        genre_mov[v]=l_val
       
#find all the gernre of the movie 
def find_genre(id_):
	all_genre=[]
	for x in genre:
		if id_ in genre_mov[x]:
			all_genre.append(x)
	return all_genre   

#find correlation matrix genrewise	 
def genre_corelation(genre,df):
	genrecorr={}
	df_trans=df.transpose()
	for x in genre:
		y=[]
		for a in genre_mov[x]:
			if a in df_trans.index:
				y.append(a)
		children=df_trans.loc[y]
		final_children=children.dropna(axis=1,how="all")
		genrecorr[x]=final_children
	return genrecorr

#generates user to movie matrix from the ratings matrix	
def getmatrix(ratings):
	fin=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
	Ratmat=fin
	y=genre_corelation(genre,fin)
	fi={}
	for x in y:
		z=y[x].fillna(y[x].mean(axis=0))
		corr=z.transpose()
		corr_final=corr.corr(method='pearson')
		fi[x]=[y[x],corr_final]
	return fin,fi


#calculates the count of common ovies of the users       
def common(user1,user2):
    return um_c.loc[user1].dot(um_c.loc[user2])

#calculates the sorted list of corlated users
def top(user,corr):
	res=corr.loc[user]
	final_res=dict()
	for x in range(len(res)):
		final_res[res.iloc[x]]=x+1
	res=sorted(list(res),reverse=True)
	re=[]
	for x in range(len(res)):
		if(final_res[res[x]]!=user):
			re.append((final_res[res[x]],res[x]))
	return re

#calculates the rating of a user for a movie based on the corelated user found by the above function
def calculate_rating(fin,final,res,user,movie):
    corr_sum=0
    pi_pm=0
    movie=movie
    user=user
    wt=0
    x=0
    y=0
    while y<15 and x<len(res):
        if res[x][0] in final.index and res[x][0] in um_withnan.index:
            if not (np.isnan(final.loc[res[x][0],movie])):
                if not (np.isnan(um_withnan.loc[res[x][0],movie])):
                    wt=common(user,res[x][0])
                    if wt==0:
                        wt=1
                    corr_sum+=(wt*res[x][1])
                    t = final.loc[res[x][0],movie]*(wt*res[x][1])
                    wt=0
        x=x+1

    mu_rating = final.loc[user]
    mu_rating = mu_rating.mean(axis=0)
    return pi_pm,corr_sum

#it calculates the rating of a user for a movie based on the corelated user found by the above function and preforms some memoiztation or faster calculation by storing the top user list alredy calculated and using them again
g=[]
def evaluate(fin,tr,userID,movieID):
	set=False
	usertop_n=None
	genres=find_genre(movieID)
	ta=0
	tb=0
	for gen in genres:
		if userID in tr[gen][1].index and movieID in tr[gen][0].columns:
			for i in g:
				if i[0]==gen and i[1][0]==userID:
					set=True
					usertop_n=i[1][1]
					break
			if set==False:
				usertop_n=top(userID,tr[gen][1])
				g.append((gen,(userID,usertop_n)))
			a,b=calculate_rating(fin,tr[gen][0],usertop_n,userID,movieID)
			ta+=a
			tb+=b
	if tb==0:
		mean=ratmat.mean(axis=1)
		mmean=ratmat.mean(axis=0)
		ome=mean.mean()
		return mmean[movieID]+(mean[userID]-ome)
	return ta/tb
  
 #it generates fold of the dataset. it divied the data into  five chunks randomly. 
def genfolds(Ratings):
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
	return folds

#calculates the mean error by running the folds and calulating the error and finding the mean eroor of the folds.
def MAE():
    folds=genfolds(Ratings)
    d_er={}
    d_oer={}
    overall=0	
    ocount=0
    for i in range(5):
        test=folds[i]
        train=Ratings.drop(list(test.index.values),axis=0)
        fin,tr=getmatrix(train)
        mae_sum=0
        count=0
		
        for val in list(test.index.values):
            re=evaluate(fin,tr,int(test.loc[val,'userId']),int(test.loc[val,'movieId']))
            if re>5:
                re=5
            if re!=-1:
                mae_sum+=abs(test.loc[val,'rating'] - re)
                count+=1
        print("After one iteration without changing Top_N Mean absolute Error :"+str(mae_sum/count))
        overall+=mae_sum
        ocount+=count
        d_er.update({i+1 : mae_sum/count})
    print("Overall without changing Top_N Mean absolute Error :"+str(overall/ocount))
    d_oer.update({"average": overall/ocount})
    return d_er,d_oer


#OUPUT WORKINGS
er,oer=MAE()
fields = ['No. of Fold', 'MAE'] 
mydict =[]
app={'No. of Fold':0,'MAE':0}
app2={'No. of Fold':'x','MAE':0}
for j in er:
    app={'No. of Fold': j,'MAE':er[j]}
    mydict.append(app)

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
	


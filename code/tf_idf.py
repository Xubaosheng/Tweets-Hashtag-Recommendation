import nltk
import string
import re
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time

# get the training data
def trainingData(path):
    time0 = time.time()
    f1 = open(path, 'r')
    data = f1.read().split('\n')
    tweetHashtag = {}
    tweetDict = {}
    tweets = []
    print len(data)
    for i in range(0, len(data)):
        tweet = data[i]
        [new_tweet, hashtag] = dataProcessing(tweet)
        if len(hashtag) > 0:
            tweetDict[i] = new_tweet
            tweets.append(new_tweet)
            tweetHashtag[new_tweet] = hashtag


    return tweets, tweetHashtag

# data pre-process
def dataProcessing(tweet):
    punctuation = string.punctuation
    punctuation = punctuation.replace('#','')
    punctuation = punctuation.replace('@','')
    stemmer = PorterStemmer()
    stopwords = nltk.corpus.stopwords.words('english') + ['u','im','rt','ummm','b','dont', 'arent','ya','yall','isnt'
                                                              ,'cant','couldnt','wouldnt','wont', 'yr','aint','gonna','ur',
                                                              'didnt','r','wasnt','werent','might','maybe','doesnt','would','shes'
                                                              ,'hes','youre', 'omg']

    tweet = tweet.replace('#', ' #')
    tweet = " ".join(tweet.split())
    if '#' in tweet:
        tweet = tweet.translate(string.maketrans("",""),punctuation)
        complier1 = re.compile('#[\w]+')
        hashtag = re.findall(complier1,tweet)
        hashtag = list(set(hashtag))
        for h in hashtag:
            if h in tweet:
                id = tweet.index(h)
                if id + len(h) < len(tweet) -1:
                    if tweet[id+len(h) +1] != '#':
                        tweet = tweet.replace(h,h[1:])
                    else:
                        tweet = tweet.replace(h,'')
                else:
                    tweet = tweet.replace(h,'')
        new_tweet = re.sub('@[\w]+', '',tweet)
        new_tweet = re.sub('[\d]+', '',new_tweet)
        re.sub(r'[^\x00-\x7F]+','', new_tweet)
        new_tweet = re.findall('[\w]+',new_tweet)
        new_tweet = [stemmer.stem(word) for word in new_tweet if word not in stopwords]
        new_tweet = " ".join(new_tweet)


        return new_tweet, hashtag
    else:
        return '',[]

# get the top ten recommended hashtags
def hashtagRecommend(tweet, tfidf, tfidf_matrix, tweets, tweetHashtag):
    topTenHashtags = []
    tweet_tfidf = tfidf.transform([tweet])
    scores = cosine_similarity(tweet_tfidf,tfidf_matrix)[0]
    tweetWithScore = []
    for i in range(0, len(scores)):
        tweetWithScore.append((tweets[i], scores[i]))

    tweetWithScore = sorted(tweetWithScore, key= lambda tweetWithScore: tweetWithScore[1], reverse= True)
    num = 0
    # print tweetWithScore[0][0]
    for i in range(0, len(scores)):
        hashtags = tweetHashtag[tweetWithScore[i][0]]
        for j in range(0, len(hashtags)):
            topTenHashtags.append(hashtags[j])
            num +=1
            if num == 10:
                break
        if num ==10:
            break
    return topTenHashtags

# compute the accuracy of hashtag prediction
def accuracy(data, tfidf, tfidf_matrix, tweets, tweetHashtag):

    correctNum = 0
    totalNum = 0

    for i in range(0, len(data)):
        time0 = time.time()
        tweet = data[i]
        print tweet
        [tweet, hashtags] = dataProcessing(tweet)
        if len(tweet) > 0:
            correct = False
            totalNum += 1
            hashtagRecommended = hashtagRecommend(tweet, tfidf, tfidf_matrix, tweets, tweetHashtag)
            for hashtag in hashtags:
                if hashtag in hashtagRecommended:
                    correctNum += 1
                    correct = True
                    break
            # print tweet
            # print hashtags
            print correct, hashtagRecommended
            # print 'recursion time:', time.time() - time0
            print ''
    print 'correct:', correctNum, 'totalNum:', totalNum
    return float(correctNum)/ totalNum




def main():
    time0 = time.time()
    tfidf_vectorizer = TfidfVectorizer(use_idf=True,ngram_range=(1,1))
    [tweets, tweetHashtag] = trainingData('tweetsWithHashtag.txt')
    # print len(tweets)
    tfidf_matrix = tfidf_vectorizer.fit_transform(tweets)
    # print 'time1:', time.time() - time0
    f = open('test_sample.txt', 'r')
    data = f.read().split('\n')

    ac = accuracy(data, tfidf_vectorizer, tfidf_matrix, tweets, tweetHashtag)
    print ac
    print 'total time:', time.time()-time0


if __name__ == '__main__':
    main()
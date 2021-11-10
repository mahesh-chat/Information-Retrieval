import os
import string
import numpy as np
from collections import Counter
from natsort import natsorted
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from nltk import word_tokenize
from nltk.stem import PorterStemmer
import nltk
nltk.download('punkt')
nltk.download('stopwords')


path = r'./document'

dataArr = []
fileMap = {}
noOfFiles = 0
for fl in os.listdir(path):
    flToRead = path + "/" + fl
    # print(flToRead)
    text = open(flToRead, 'r')
    dataArr.append(text.read())
    fileMap[noOfFiles] = flToRead
    noOfFiles += 1

nData = ''
for i in range(len(dataArr)):
    tm = dataArr[i].casefold()
    nData += tm

stop = set(stopwords.words('english') + list(string.punctuation))
a = [i for i in word_tokenize(nData) if i not in stop]

dWords = Counter(a)

sortWords = sorted(dWords.items(), key=lambda x: x[1], reverse=True)

# converting list of tuples to dictionary
sortWords = dict(sortWords)
# getting keys of dict to array
l = []
for i in sortWords.keys():
    l.append(i)

# stemming
p = PorterStemmer()
stems = []
for it in l:
    tmp = p.stem(it)
    if tmp not in stems:
        stems.append(tmp)

fDict = {}
for i in range(noOfFiles):
    txthere = dataArr[i].lower()
    for item in stems:
        if item in txthere:
            if item not in fDict:
                fDict[item] = []
            if item in fDict:
                fDict[item].append(i+1)


def read_file(filename):
    with open(filename, 'r') as f:
        stuff = f.read()
    f.close()
    # Remove header and footer.
    stuff = remove_header_footer(stuff)
    # print(stuff)
    return stuff


def remove_header_footer(final_string):
    new_final_string = ""
    tokens = final_string.split(' ')
    # Remove tokens[0] and tokens[-1]
    for token in tokens[1:-1]:
        new_final_string += token+" "
    return new_final_string


def preprocessing(final_string):
    # Tokenize.
    tokenizer = TweetTokenizer()
    token_list = tokenizer.tokenize(final_string)

    # Remove punctuations.
    table = str.maketrans('', '', '\t')
    token_list = [word.translate(table) for word in token_list]
    punctuations = (string.punctuation).replace("'", "")
    trans_table = str.maketrans('', '', punctuations)
    stripped_words = [word.translate(trans_table) for word in token_list]
    token_list = [str for str in stripped_words if str]
    token_list = [word.lower() for word in token_list]
    return token_list


folder_names = ["document"]
stemmer = PorterStemmer()
fileno = 0
pos_index = {}
file_map = {}
for folder_name in folder_names:

    file_names = natsorted(os.listdir("./" + folder_name))

    for file_name in file_names:
        stuff = read_file("./" + folder_name + "/" + file_name)

        final_token_list = preprocessing(stuff)

        for pos, term in enumerate(final_token_list):
            term = stemmer.stem(term)
            if term in pos_index:

                pos_index[term][0] = pos_index[term][0] + 1

                if fileno in pos_index[term][1]:
                    pos_index[term][1][fileno].append(pos)

                else:
                    pos_index[term][1][fileno] = [pos]

            else:

                # Initialize the list.
                pos_index[term] = []
                # The total frequency is 1.
                pos_index[term].append(1)
                # The postings list is initially empty.
                pos_index[term].append({})
                # Add doc ID to postings list.
                pos_index[term][1][fileno] = [pos]
        file_map[fileno] = "./" + folder_name + "/" + file_name
        fileno += 1


def srcPosi(searchText):
    sample_pos_idx = stemmer.stem(searchText)
    sample_pos_idx = pos_index[sample_pos_idx]

    # print("Positional Index")
    # print(sample_pos_idx)

    file_list = sample_pos_idx[1]
    op = [*file_list]

    # print("Filename, [Positions]")
    # for fileno, positions in file_list.items():
    #     print(file_map[fileno], positions)

    return op


def srcNonPosi(searchWord_):
    pt = PorterStemmer()
    searchWord = pt.stem(searchWord_)
    if searchWord in fDict:
        return fDict[searchWord]


class InfoRet:

    @staticmethod
    def searchPosIndex(word):
        # pos_index
        searchText = word
        sample_pos_idx = stemmer.stem(searchText)
        sample_pos_idx = pos_index[sample_pos_idx]
        response = {}
        response["PositionIndex"] = sample_pos_idx[0]
        response["data"] = {}

        file_list = sample_pos_idx[1]
        for fileno, positions in file_list.items():
            response["data"][file_map[fileno]] = positions

        return response

    @staticmethod
    def searchNonPosIndex(word):
        searchWord_ = word
        pt = PorterStemmer()
        searchWord = pt.stem(searchWord_)
        response = []
        if searchWord in fDict:
            for f in fDict[searchWord]:
                response.append(fileMap[f-1])
        return response

    @staticmethod
    def BoolRetrivalNonPos(q):
        q = q.casefold()
        t = q.split(" ")
        t1 = t[0]
        t2 = t[2]
        operand = t[1]
        ans = []
        t1op = srcPosi(t1)
        t2op = srcPosi(t2)

        if(operand == 'and'):
            for i in t1op:
                if i in t2op:
                    ans.append(i)
        if(operand == 'or'):
            for i in t1op:
                ans.append(i)
            for i in t2op:
                ans.append(i)
        return [file_map[i] for i in list(set(ans))]

    @staticmethod
    def BoolRetrivalPos(q):
        q = q.casefold()
        t = q.split(" ")
        t1 = t[0]
        t2 = t[2]
        operand = t[1]
        ans = []
        t1op = srcPosi(t1)
        t2op = srcPosi(t2)

        if(operand == 'and'):
            for i in t1op:
                if i in t2op:
                    ans.append(i)
        if(operand == 'or'):
            for i in t1op:
                ans.append(i)
            for i in t2op:
                ans.append(i)
        if(operand == 'not'):
            for i in t1op:
                if i not in t2op:
                    ans.append(i)
        return [file_map[i] for i in list(set(ans))]

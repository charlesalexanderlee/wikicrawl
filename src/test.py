def split_list(_list, n=1):
    return [
        _list[i*len(_list)//n : (i+1)*len(_list)//n] 
        for i in range(n)
    ]


original_data = ['This', 'is', 'the', 'original', 'list', 'of', 'data', 'or', 'the', 'original', 'data', 'list', 'This', 'is', 'the', 'original', 'list', 'of', 'data', 'or']
threads = 10

for idx, l in enumerate(split_list(original_data, threads)):
    print(idx+1, l)
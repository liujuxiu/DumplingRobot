import jieba.posseg as pseg
filter_list=['uz','uj','ul','e','y','x','ud','u','zg']#词性标注 过滤语气词
#分词、过滤语气词、并转化为元组
def segmentation(segm):
    segs = pseg.cut(segm)
    seg_list=[]
    for w in segs:
        #print('%s %s' % (w.word, w.flag))
        if w.flag not in filter_list:
            seg_list.append(w.word)
    segtuple=tuple(seg_list)
    return (segtuple)

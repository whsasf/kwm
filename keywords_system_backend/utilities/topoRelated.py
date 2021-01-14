

# this function is used to get connected words based on one given basicWord
async def jisuan(init,items):
            tempLength = len(items)
            loopReault = [{} for i in range(0,tempLength)]
            for index in range(0,tempLength):
                loopReault[index]['name'] = items[index]['word']
                if items[index]['status'] == '停止':
                    loopReault[index]['label'] = { "backgroundColor" : 'red'}
                elif items[index]['status'] == '已添加':
                    loopReault[index]['label'] = { "backgroundColor" : 'green'}
                else:
                    loopReault[index]['label'] = { "backgroundColor" : 'blue'}
                
                if items[index]['word'] == word:
                    #  查询的 基词 放大显示
                    loopReault[index]['label']['fontSize'] = 40
                    loopReault[index]['label']['lineHeight'] = 40

                init.append(loopReault[index])

                # 1-2 分析每一个 词  有没有 拓展词
                queryDict = {'mword': items[index]['word']}
                result = await fetchExtendedWords(dbPrefix+'-'+projectId,'extendedWords',xfilter= queryDict,xshown = shownDict)
                result = result['content']
                #print('loopReault',loopReault)
                #print('result',result)
                if len(result) == 0:
                    #print('退出')
                    # 空，无须往下进行了，退出，
                    pass
                else:
                    # 继续进行
                    #print('继续')
                    
                    init[index]['children'] = []

                    loopReault[index]['children'] = []
                    await jisuan(loopReault[index]['children'],result)
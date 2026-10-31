new=[]
def q(prompt,correct,b,c,d,explain,evidence):
    return dict(prompt=prompt,choices=[correct,b,c,d],answer=0,explain=explain,evidence=evidence)
def add(level,title,ja,uk,questions,vocab,grammar):
    i=sum(x['level']==level for x in new)+1
    new.append(dict(id=f'{level[0]}131-{i:02}',level=level,title=title,ja=ja.strip(),uk=uk.strip(),questions=questions,vocab=vocab,grammar=grammar))

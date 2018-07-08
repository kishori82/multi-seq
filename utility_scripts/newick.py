import sys


B = []

with open( sys.argv[1], 'r') as fin:
   for line in fin:
     tax =  line.strip().split('\t')[38]
     fields=["root"]
     for x in tax.split(';'):
        fields.append(x.strip()) 
     B.append(fields)

S1=[]
S1.append("(")
S1.append("root")
S2=[]
S2.append(';')
S2.append(')')

k=0
s = len(B)
m= [0 for x in range(0, s) ]
M= [ len(B[x]) for  x in range(0, s) ]

while k < s:
   if len(S1)==0:
     break
   c = S1.pop()

   if c == '(':
     S2.append(c)
     continue

   D={}
   k=0
   seen ={}
   for i in range(0, s):
     if m[i]==M[i]-1:
       k += 1
       continue
     if c == B[i][m[i]]:
        m[i] += 1
        if m[i] < M[i] - 1:
          if not  B[i][m[i]]  in seen:
            D[B[i][m[i]]]= True
        else:
         if not  B[i][m[i]]  in seen:
           S2.append(B[i][m[i]])

        seen[B[i][m[i]]]= True
             

   if len(D)>0:
     S1.append('(')
     for d in D:
        S1.append(d)

     if S2[-1]!=')':
          S2.append(',')
     S2.append(')')
   else:
     if S2[-1]!=')':
         S2.append(',')
     S2.append(c)

S3= [ x for x in reversed(S2) ]
print ' '.join(S3)
   

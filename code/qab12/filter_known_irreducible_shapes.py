#!/usr/bin/env python3
import argparse,csv,math
from pathlib import Path

def factor(n):
 out=[];p=2
 while p*p<=n:
  if n%p==0:
   out.append(p)
   while n%p==0:n//=p
  p=3 if p==2 else p+2
 if n>1:out.append(n)
 return out
def rad(n):return math.prod(factor(n))
def isprime(n):
 if n<2:return False
 if n%2==0:return n==2
 p=3
 while p*p<=n:
  if n%p==0:return False
  p+=2
 return True
def powerful(n,r):return n%(r*r)==0
def known(a,b,n,ra,rb):
 x,y=sorted((a,b));rx,ry=(ra,rb) if a<=b else (rb,ra)
 if x>1 and rx==x and ry==y:return True
 if x==2 or y==2:return True
 if x==1 and rad(n)==n:return True
 if isprime(n):return True
 if n%2==0 and n>4 and isprime(n//2):return True
 if x>1 and not powerful(x,rx) and y>=x*max(11.21685874,math.log2(x)):return True
 return False
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
with a.input.open(newline='') as f, a.output.open('w',newline='') as g:
 rd=csv.DictReader(f);wr=csv.DictWriter(g,fieldnames=rd.fieldnames);wr.writeheader();total=kept=0
 for row in rd:
  total+=1
  A,B,N,ra,rb=map(int,[row['a'],row['b'],row['n'],row['rad_a'],row['rad_b']])
  if known(A,B,N,ra,rb):continue
  wr.writerow(row);kept+=1
print(f'input_shapes={total} reducible_candidate_shapes={kept}')

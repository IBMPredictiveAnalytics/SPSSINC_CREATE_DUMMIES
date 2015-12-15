begin program.
import SPSSINC_CREATE_DUMMIES
reload(SPSSINC_CREATE_DUMMIES)
end program.

dataset close all.
new file.



get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat
ROOTNAME = job
/OPTIONS ORDER=A USEVALUELABELS=YES.

* two variables.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat gender
ROOTNAME = job gen
/OPTIONS ORDER=A USEVALUELABELS=YES.

* one- and two-way interactions.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat gender
ROOTNAME = job gen ROOTNAME2=two
/OPTIONS ORDER=A USEVALUELABELS=YES.

* three way.  No lower orders.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat gender minority
ROOTNAME3=three
/OPTIONS ORDER=A USEVALUELABELS=YES.

* 1, 2, and 3 way.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat gender minority
rootname = job gen min rootname2 = two ROOTNAME3=three
/OPTIONS ORDER=A USEVALUELABELS=YES.

* use values instead of labels.
* 1, 2, and 3 way.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat gender minority
rootname = job gen min rootname2 = two ROOTNAME3=three
/OPTIONS ORDER=A USEVALUELABELS=NO.

* scale variables.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat salary
rootname = job gen rootname2 = two
/OPTIONS ORDER=A USEVALUELABELS=NO.

* encoding tests.
dataset close all.
new file.
set unicode on locale=english.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
add value lables gender 'm' 'mäe'.
rename variable salary= sálàry.
SPSSINC CREATE DUMMIES VARIABLE=jobcat gender sálàry
rootname = job gen sal rootname2 = two ROOTNAME3=three
/OPTIONS ORDER=A USEVALUELABELS=YES.

dataset close all.
new file.
set unicode off locale=english.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
add value lables gender 'm' 'mäe'.
rename variable salary= sálàry.
SPSSINC CREATE DUMMIES VARIABLE=jobcat gender sálàry
rootname = job gen sal rootname2 = two ROOTNAME3=three
/OPTIONS ORDER=A USEVALUELABELS=yes.
exec.

* macro definition and report.
dataset close all.
new file.
set unicode on.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat educ
ROOTNAME = job ed
/OPTIONS ORDER=A USEVALUELABELS=YES
MACRONAME= "!job" "!ed".

* macrodef - protect scale vars.
spssinc create dummies variables = salary salbegin
rootname = sa sb rootname2=two
/options macroname = "!sa" "!sb" macroname2="!two".

* prune macro names.
spssinc create dummies variables = educ salbegin
rootname = ed sal rootname2=two
/options macroname = "!ed" "!sal" macroname2="!two".

spssinc create dummies variables = jobcat minority gender
rootname = j m g rootname2=two rootname3=three
/options macroname1="!j !m !g" macroname2="!two" macroname3="!three".
REGRESSION
  /STATISTICS COEFF
  /DEPENDENT salary
  /METHOD=ENTER !j !m !g !two.

REGRESSION
  /STATISTICS COEFF
  /DEPENDENT salary
  /METHOD=ENTER !j !m !g !two !three.

*mixed scale, cat with macro w exclusion.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
spssinc create dummies variables = jobcat minority prevexp
rootname = j m p rootname2=two rootname3=three
/options macroname1="!j !m !p" macroname2="!two" macroname3="!three".
regression /statistics=coef /dependent = salary
/method=enter !j !m !p !two.

get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
spssinc create dummies variables =  minority prevexp
rootname = j p.

get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
spssinc create dummies variables = minority gender
rootname = m g rootname2=two
/options macroname1="!j !m" macroname2="!two".
regression /dependent salary /method=enter !j !m !two.

* descending order with macro deletion.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
spssinc create dummies variables = minority gender
rootname = m g rootname2=two
/options order=d macroname1="!j !m" macroname2="!two".
regression /dependent salary /method=enter !j !m !two.

get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat educ
ROOTNAME = job ed rootname2=two
/OPTIONS ORDER=A USEVALUELABELS=YES
MACRONAME= "!job" "!ed" macroname2="!two".

get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES VARIABLE=jobcat minority gender
rootname3=three
/OPTIONS ORDER=A USEVALUELABELS=YES
macroname3="!three".

* error handling - no variables.
get file="c:/spss20/samples/english/employee data.sav".
dataset name emp.
SPSSINC CREATE DUMMIES 
rootname3=three
/OPTIONS ORDER=A USEVALUELABELS=YES


DATASET ACTIVATE emp.
SPSSINC CREATE DUMMIES VARIABLE=educ 
/OPTIONS ORDER=A USEVALUELABELS=YES USEML=YES
MACRONAME2="!abc".



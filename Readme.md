# SPSSINC CREATE DUMMIES
## Create a set of dummy variables representing the values of on
 This procedure creates a set of 0-1 dummy variables repre  senting the distinct values of one or more variables. It can also cre  ate dummies for two- and three-way interaction terms.  It is useful,   for example, in converting categorical variables into a set of variab  les appropriate for use in the Regression procedure. It can optionall  y create  macro variables representing sets of dummies.

---
Requirements
----
- IBM SPSS Statistics 18 or later

---
Installation intructions
----
1. Open IBM SPSS Statistics
2. Navigate to Utilities -> Extension Bundles -> Download and Install Extension Bundles
3. Search for the name of the extension and click Ok. Your extension will be available.

---
Tutorial
----
Create a set of dummy variables for values of one or more variables

SPSSINC CREATE DUMMIES  VARIABLES=*variables* ROOTNAME1=*rootnames*
ROOTNAME2=*rootname* ROOTNAME3=*rootname*

/OPTIONS MAXVARS=*n* ORDER=A^&#42;&#42; or D   
MACRONAME1="*name*" MACRONAME2="*name*" MACRONAME3="*name*"  
OMITFIRST=YES^&#42;&#42; or NO  
USEVALUELABELS=NO^&#42;&#42; or YES  
USEMLS=YES^&#42;&#42; or NO

/HELP

^&#42; Required  
^&#42;&#42; Default

SPSSINC CREATE DUMMIES /HELP displays this help and does nothing else.

Example:
```
SPSSINC CREATE DUMMIES VARIABLES=job gender
ROOTNAME1 = jobroot genderroot  ROOTNAME2=two
MACRONAME1 = "!job" "!gender".
```

This command creates a set of 0-1 dummy variables for values of one or more variables.  This can include
dummies for individual variables, two-way interactions, and three-way interactions.  This is 
useful, for example, when running the Regression procedure and you have categorical 
variables that needs to be treated as factors.  Scale measurement variables can be included
and are treated appropriately for interaction terms.

Any cases excluded by the current filter are not considered in determining the set of values.

**VARIABLES** specifies the variables for which dummies are created.
**ROOT1** specifies root names for the one-way dummy variables.  Specify one root name
for each variable listed in VARIABLES.  **ROOT2** and **ROOT3** each specify a single root name
for all two-way or three-way effects, respectively.  Only orders for which there is a root
name are generated.

For one-way dummies, the dummy names will have the form
```rootname_n```.  Names for two-way and three-way dummies have the form
```rootname_m_n```, and ```rootname_m_n_o```.
Existing variables will be replaced.

For a scale variable, the one-way generated variable is just a copy rather than a
set of individual dummies.  For two-way dummies, for example, if x is scale 
and y is categorical with values 1, 2, and 3, the two-way interaction 
would generate
```x*(y eq 1), x * (y eq 2), and x*(y=3)```.

OPTIONS
-------
Specify **USEMLS**=NO to force all variables to be treated categorically.

Specify **MAXVARS**=n to limit the number of dummy variables generated to 
no more than n.  This applies only to the one-way interactions.

By default the dummies correspond to ascending values of the 
input variable.  Specify **ORDER**=D for the reverse order.  For interaction dummies, the
values are sorted in the order in which the variables are listed in the VARIABLES
keyword.

The variable labels for the new variables have forms like
```varname = value or (varname = value) * (varname = value)``` or 
```varname * (varname = value)```.

**USEVALUELABELS**=YES causes the value label corresponding to the dummy 
to be used in the label.  If a value does not have a label, the value itself is used.
USEVALUELABELS=NO causes the values to be used instead.

**MACRONAME1**=name creates a set of macros whose text is the list of dummy variables.
The number of names must match the number of variables.
**MACRONAME2** and **MACRONAME3** specify a single name each for the 
two- and three-way macros.  Note that the macro names must be enclosed in
quotes. (Otherwise the system would attempt to expand them.)  However, you
can use one set of quotes surrounding the entire list as a shortcut.

By default, the first dummy (after apply the order specification) is omitted
from  the list for each macro .  This is convenient in Regression if a 
constant term is included.  Specify **OMITFIRST**=NO to include all the variables 
in the macro text.

**ROOTNAME** is a synonym for ROOTNAME1; **MACRONAME** is a synonym
for MACRONAME1, and **VARIABLE** is a synonym for VARIABLES.

---
License
----

- Apache 2.0
                              
Contributors
----

  - JKP, IBM SPSS

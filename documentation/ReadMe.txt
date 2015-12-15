This zip file contains the materials for the extension command

SPSSINC CREATE DUMMIES.


The command provides a procedure for creating a set of dummy variables representing the distinct values of a variable.  It is useful, for example, in converting a categorical variable into a set of variables appropriate for use in the Regression procedure.

This material requires 
SPSS Statistics 17 and 
the Python plug-in.

It includes a dialog box definition, a help file, the syntax definition, and the

implementation file.




To install this procedure for Version 17 or later, unzip all of the files into the extensions subdirectory
 of your SPSS Statistics installation.  Next, in SPSS Statistics, use
Utilties>Install Custom Dialog

to add this item to the menus.

The dialog box will appear on the Transform menu.

Executing

SPSSINC CREATE DUMMIES /HELP.

will display the complete syntax help.


This command has not been tested with Version 16, but it should work with two minor changes.
First, rename SPSSINC_CREATE_DUMMIES.py to DUMMIES.py.  
Rename the xml file similarly.

Second, in the xml file, change the command name to DUMMIES.
Place the Python file in your site-packages directory rather than in the extensions directory.  The dialog box, of course, will not be available in Version 16.


Questions and comments should be directed to the SPSS Developer Central Python
 Programmability forum.
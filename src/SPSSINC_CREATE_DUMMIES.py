#/***********************************************************************
# * Licensed Materials - Property of IBM 
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2014
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp. 
# ************************************************************************/

from __future__ import with_statement

"""SPSSINC CREATE DUMMIES extension command"""

__author__ =  'spss, JKP'
__version__=  '2.0.3'

# history
# 18-dec-2009 enable translation
#  23-jun-2010  translatable proc names
#  31-oct-2011 upgrade to support two and three way interaction term generation
# 15-may-2013 fix case where label is null and generation from labels is requested

helptext = """SPSSINC CREATE DUMMIES  VARIABLES=varnames ROOTNAME1=rootnames
ROOTNAME2=rootname ROOTNAME3=rootname
[/OPTIONS [MAXVARS=n] [ORDER={A*|D}] 
[MACRONAME1=name] [MACRONAME2=name] [MACRONAME3 = name] OMITFIRST={YES*|NO}
[USEVALUELABELS={NO*|YES}] [USEMLS={YES*|NO}]
[/HELP]

Example:
SPSSINC CREATE DUMMIES VARIABLES=job gender
ROOTNAME1 = jobroot genderroot  ROOTNAME2=two
MACRONAME1 = "!job" "!gender".

Create a set of 0-1 dummy variables for values of one or more variables.  This can include
dummies for individual variables, two-way interactions, and three-way interactions.  This is 
useful, for example, when running the Regression procedure and you have categorical 
variables that needs to be treated as factors.  Scale measurement variables can be included
and are treated appropriately for interaction terms.

Any cases excluded by the current filter are not considered in determining the set of values.

VARIABLES specifies the variables for which dummies are created.
ROOT1 specifies root names for the one-way dummy variables.  Specify one root name
for each variable listed in VARIABLES.  ROOT2 and ROOT3 each specify a single root name
for all two-way or three-way effects, respectively.  Only orders for which there is a root
name are generated.

For one-way dummies, the dummy names will have the form
rootname_n.  Names for two-way and three-way dummies have the form
rootname_m_n, and rootname_m_n_o.
Existing variables will be replaced.

For a scale variable, the one-way generated variable is just a copy rather than a
set of individual dummies.  For two-way dummies, for example, if x is scale 
and y is categorical with values 1, 2, and 3, the two-way interaction 
would generate
x*(y eq 1), x * (y eq 2), and x*(y=3).
Specify USEMLS=NO to force all variables to be treated categorically.

Specify MAXVARS=n to limit the number of dummy variables generated to 
no more than n.  This applies only to the one-way interactions.

ORDER=A or D.  By default the dummies correspond to ascending values of the 
input variable.  Specify D for the reverse order.  For interaction dummies, the
values are sorted in the order in which the variables are listed in the VARIABLES
keyword.

The variable labels for the new variables have forms like
varname = value or (varname = value) * (varname = value) or 
varname * (varname = value).
USEVALUELABELS=YES causes the value label corresponding to the dummy 
to be used in the label.  If a value does not have a label, the value itself is used.
USEVALUELABELS=NO causes the values to be used instead.

MACRONAME1=name creates a set of macros whose text is the list of dummy variables.
The number of names must match the number of variables.
MACRONAME2 and MACRONAME3 specify a single name each for the 
two- and three-way macros.  Note that the macro names must be enclosed in
quotes. (Otherwise the system would attempt to expand them.)  However, you
can use one set of quotes surrounding the entire list as a shortcut.

By default, the first dummy (after apply the order specification) is omitted
from  the list for each macro .  This is convenient in Regression if a 
constant term is included.  Specify OMITFIRST=NO to include all the variables 
in the macro text.

ROOTNAME is a synonym for ROOTNAME1; MACRONAME is a synonym
for MACRONAME1, and VARIABLE is a synonym for VARIABLES.

/HELP displays this help and does nothing else.
"""

# prior to 18.0.2, rootnames containing extended characters in Unicode mode
# will produce an error, although the results are correct

import spss, spssaux
from extension import Template, Syntax, processcmd
import sys, locale



class DataStep(object):
    def __enter__(self):
        """initialization for with statement"""
        try:
            spss.StartDataStep()
        except:
            spss.Submit("EXECUTE")
            spss.StartDataStep()
        return self
    
    def __exit__(self, type, value, tb):
        spss.EndDataStep()
        return False


def CreateBasisVariables(varname=None, varnames=None, root=None, root1=None, root2=None, root3=None,
    maxvars=None, usevaluelabels=True, macroname=None, macroname1=None, macroname2=None, macroname3=None,
        omitfirst=True, usemls=True, order="a", labelseparator=": "):
    """Create a set of dummy variables that span the values of varname within any current filter.
    
    varname is a list of variable names.
    This function works for numeric and string variables except those with date or time format.  
    The new variables are named root_n, starting with n=1 in ascending value order (by default).
    Any existing variables with these names are overwritten.
    Each variable is labeled with the underlying variable name and the value it represents.
    If usevaluelabels is True, the value label, if any, is used in place of the value. Since the new
    label will contain the name of the underlying variable, the underlying label may be truncated.

    Missing values are ignored.
    If maxvars is specified, no more than maxvars will be created for each group

    If macroName is specified, an SPSS macro with that name will be
    produced containing the names of the created dummy variables.
    If omitfirst is true, the first root variable is omitted (making the reference 
    category the first one).  The meaning of first depends on the order parameter.
    If order="D", the categories are in descending order, and the reference (omitted)
    category will the last one.
    Generated labels have the form variable = value by default.  labelseparator can be used to
      choose a different separator, e.g., labelseparator=": ".
    """
    
        # debugging
    # makes debug apply only to the current thread
    #try:
        #import wingdbstub
        #if wingdbstub.debugger != None:
            #import time
            #wingdbstub.debugger.StopDebug()
            #time.sleep(2)
            #wingdbstub.debugger.StartDebug()
        #import thread
        #wingdbstub.debugger.SetDebugThreads({thread.get_ident(): 1}, default_policy=0)
        ## for V19 use
        ##    ###SpssClient._heartBeat(False)
    #except:
        #pass
    
    # legacy name mapping
    if (varname and varnames)\
       or (root and root1)\
       or (macroname and macroname1):
        raise ValueError(_("""Cannot use both VARIABLE and VARIABLES or ROOTNAME and ROOTNAME1
or MACRONAME and MACRONAME1 together"""))
    if varname:
        varnames = varname
    if root1:
        root = root1
    if macroname1:
        macroname = macroname1
        
    if varnames is None:
        raise ValueError(_("""At least one variable must be specified"""))
    roots = [root, root2, root3]
    numvar = len(varnames)
    if not any(roots):
        raise ValueError(_("""No dummy variable creation was specified"""))
    rootlist = []
    for i, item in enumerate(roots):
        if item is not None:
            if i+1 > numvar:
                raise ValueError(_("""Not enough variables selected to produce %s-way interaction""") % (i+1))
            rootlist.append(item)
            if i == 0 and len(item) != numvar:
                raise ValueError(_("""The number of root names does not match the number of variables: %s""") % item)
        else:
            rootlist.append([])
    global  unistr
    if spss.PyInvokeSpss.IsUTF8mode():
        unistr = unicode
    else:
        unistr = str
        
    # When generating macros, for one-way dummies, there must be a macro name
    # for each variable.  For interaction dummies, there is one macro name for all dummies of that order
    if macroname and root is not None:  # main effects
        if len(macroname) == 1:
            macroname = macroname[0].split()  #dialog generates a single set of quotes around entire list of names
        if len(macroname) != len(root):
            raise ValueError(_("""For main-effect dummies, the number of macro names is different from the number of variables."""))
    macronames = [macroname, macroname2, macroname3]
    if any([item[0] and not item[1] for item in zip(macronames, rootlist)]):
        raise ValueError(_("""A macro name was specified without a corresponding root name"""))
    
    maker = Maker(varnames, rootlist, macronames, maxvars, usevaluelabels, omitfirst, order,
        labelseparator, usemls)
    
    syntax = maker.buildsyntax()
    spss.Submit(syntax)
    maker.report()
    maker.macros()



class Vp(object):
    """structure for variable properties"""
    
    def __init__(self, vtype, vlabels, generate):
        """vtype is >0 for strings
        vlabels is a value label dictionary or None
        generate indicates whether to generate a var = value expression
        or just use the name"""
        
        attributesFromDict(locals())
        
class Maker(object):
    """Create dummy variables for levels of selected variables"""
    
    def __init__(self, varnames, rootlist, macronames, maxvars, usevaluelabels, omitfirst, order,
        labelseparator, usemls):
        attributesFromDict(locals())

        self.index = []  # variable indexes
        self.oneway = len(rootlist[0]) > 0
        self.twoway = len(rootlist[1]) > 0
        self.threeway = len(rootlist[2]) > 0
        self.numvar = len(varnames)
        self.one = 1
        self.two = 1
        self.three = 1
        # for discarding smallest or largest value in macro generation
        self.minormax = order == 'a' and min or max
        self.extreme = [None for i in range(len(varnames))]   # indexed by var index
        self.exclude = set()   # record target variable names involving categorical values that will be excluded if using omitfirst
        # dict of target variable names indexed by order
        # for 1-way entries, entry is a list of lists
        self.target = {}
        self.target[1] = []
        for i in range(len(varnames)):
            self.target[1].append([])
        self.target[2] = []
        self.target[3] = []
        # track target variables involving no categorical expressions
        # these are exempt from pruning in macro generation
        self.onlyscale = set() 
        self.myenc = locale.getlocale()[1]  # get current encoding in case conversions needed
        with DataStep():
            ds = spss.Dataset(name="*")
            ###ds = spss.Dataset()
            self.varprops = {}
            self.data = set()
            for i, var in enumerate(varnames):
                v = ds.varlist[var]
                vfmt = v.format
                if vfmt.find("DATE") >= 0 or vfmt.find("TIME") >= 0:
                    raise AttributeError(_("SPSSINC CREATE DUMMIES cannot be used with date or time variables"))
                if usevaluelabels:
                    vlabels = dict([(k, item.replace('"', '""')) for k, item in v.valueLabels.data.items()])
                else:
                    vlabels = None
                generate = not (usemls and v.measurementLevel in ["SCALE", "UNKNOWN"])
                if not generate:
                    vlabels = {False: varnames[i]}  # label just uses variable name
                self.varprops[i] = Vp(v.type, vlabels, generate)
                self.index.append(v.index)  # maps varname location to position in case vector

            # data is a set whose members are tuples of the form ((index list), (value list))
            # where the indexes refer to the order in varnames list
            # for scale variables if honoring measurement level, all values are collapsed into one
            # sysmis values (None) are discarded
            
            for case in ds.cases:
                for i in range(self.numvar):
                    val = self.getval(i, case)
                    if val is None:
                        continue
                    self.extreme[i] = self.minmax(self.extreme[i], val)  # record extrema for macro generation
                    if self.oneway:
                        self.data.add(((i,), (val,)))
                    if self.twoway or self.threeway:
                        for j in range(i+1, self.numvar):
                            val2 = self.getval(j, case)
                            if val2 is None:
                                continue
                            if self.twoway:
                                self.data.add(((i,j), (val, val2)))
                            if self.threeway:
                                for k in range(i+j+1, self.numvar):
                                    val3 = self.getval(k, case)
                                    if val3 is not None:
                                        self.data.add(((i,j,k), (val, val2, val3)))

    def minmax(self, oldval, curval):
        """Return min or max of oldval and curval
        
        if oldval is None, curval is returned"""
        
        if oldval is None:
            return curval
        else:
            return self.minormax(oldval, curval)
        
    def getval(self, i, case):
        """return value or False depending on scale variable behavior settings
        
        i is the variable index in varnames
        case is the current case"""
        
        value = case[self.index[i]]
        if self.varprops[i].generate:
            return value
        else:
            return False
        
    labelexpr = """VARIABLE LABEL %s "%s"."""
    def buildsyntax(self):
        """return syntax for dummy creation and variable labels.  Ignore None (sysmis) values"""
        
        syntax = []
        for varspec, valuespec in sorted(self.data):
            order = len(varspec)
            target, compute = self.makecompute(varspec, valuespec)
            syntax.append(compute)
            # assemble label of form varname=value [and varname=value]
            # if the label exceeds maximum length, it will be truncated and Statistics will issue a warning message
            # for non-generate variables, just use variable name
            labellist = []
            if self.usevaluelabels:
                for i, var in enumerate(varspec):
                    if self.varprops[var].generate:
                        lbl = self.varprops[var].vlabels.get(valuespec[i], self.fstrip(valuespec[i]))
                        if isinstance(lbl, float):
                            lbl = str(lbl)
                        labellist.append(self.varnames[var] + "=" + lbl)
                        #labellist.append(self.varnames[var] + "=" + self.varprops[var].vlabels.get(valuespec[i], self.fstrip(valuespec[i])))
                    else:
                        labellist.append(self.varnames[var])
            else:
                for i, var in enumerate(varspec):
                    if self.varprops[var].generate:
                        labellist.append(self.varnames[var] + "=" + unistr(self.fstrip(valuespec[i])))
                    else:
                        labellist.append(self.varnames[var])
                #labellist = [self.varnames[var] + "=" + unistr(valuespec[i]) for i, var in enumerate(varspec)]
            syntax.append(Maker.labelexpr % (target, _safeval(" * ".join(labellist), '"')))
        return syntax
    
    def makecompute(self, vnindexes, valuelist):
        """Return a compute statement
        
        vnindexes is a list of 1 - 3 variable indexes
        valuelist is a list of 1-3 values
        None values must already have been discarded
"""
        order = len(vnindexes)
        targetname = self.maketargetname(order, vnindexes[0])

        # record whether this target variable only involves scale variables
        for i in range(order):
            if self.varprops[vnindexes[i]].generate:
                break
        else:
            self.onlyscale.add(targetname)
            
        # record names of categorical variables poisoned by reference to extreme value that will be excluded from macro
        for i in range(order):
            v = vnindexes[i]
            if self.extreme[v] == valuelist[i] and self.varprops[v].generate:
                self.exclude.add(targetname)
        if order == 1:
            compute = """COMPUTE %s = %s.""" % (targetname, self.frag(vnindexes[0], valuelist[0]))
        else:
            part1 = self.frag(vnindexes[0], valuelist[0])
            part2 = self.frag(vnindexes[1], valuelist[1])
            if order == 2:
                compute = """COMPUTE %s = (%s) * (%s).""" % (targetname, part1, part2)
            else:
                part3 = self.frag(vnindexes[2], valuelist[2])
                compute = """COMPUTE %s = (%s) * (%s) * (%s).""" % (targetname, part1, part2, part3)
                
        return targetname, compute
        
    def frag(self, vnindex, value):
        """Return equality test syntax or blank
        
        vnindex indexes the variable names list
        value is the value to test for"""
        
        if self.varprops[vnindex].vtype > 0:   # string
            quot = '"'
        else:            
            quot =  ""
        if self.varprops[vnindex].generate:
            cexp = """%s EQ %s%s%s""" % (self.varnames[vnindex], quot, _safeval(value, quot), quot)
        else:
            cexp = self.varnames[vnindex]
        return cexp
    
    def maketargetname(self, order, index):
        """Return a variable name appropriate for the order
        
        order is 1-3 indicating the interaction order
        index identifies the first variable so that 1-way roots can be selected appropriately"""
        
        if order == 1:
            target = self.rootlist[0][index]
        else:
            target = self.rootlist[order-1]
        target = target + "_" + str(self.one)
        if order == 1:
            self.one += 1
        if order >1:
            target = target+ "_" + str(self.two)
            if order == 2:
                self.two += 1
        if order > 2:
            target = target + "_" + str(self.three)
            self.three += 1
        if len(target) > 64:
            raise ValueError(_("""The length of a target name exceeds 64 bytes.  Shorten the root names."""))
        else:
            # keep track of target names by order
            if order == 1:
                self.target[1][index].append(target)
            else:
                self.target[order].append(target)
            return target
    
    def fstrip(self, value):
        """return value after stripping if string"""
        if isinstance(value, basestring):
            return value.rstrip()
        else:
            return value
        
    def report(self):
        """Display table of variables created"""
        
        info = NonProcPivotTable(omssubtype="INFORMATION", procname="SPSSINC CREATE DUMMIES",
            tabletitle=_("Variable Creation"), columnlabels=[_("""Label""")])
        
        vardict = spssaux.VariableDict()
        oneway = []
        if self.target[1]:
            for item in self.target[1]:
                oneway.extend(item)
        for var in oneway:
            info.addrow(var, [vardict[var].VariableLabel])
        for var in self.target[2]:
            info.addrow(var, [vardict[var].VariableLabel])
        for var in self.target[3]:
            info.addrow(var, [vardict[var].VariableLabel])
        try:
            info.generate()
        except:
            print """The report table could not be produced"""   # nontranslatable
        
    def macros(self):
        """Create requested macro definitions and report"""
        
        first = 1 and self.omitfirst or 0
        if not (self.macronames[0] or self.macronames[1] or self.macronames[2]):
            return
        info = NonProcPivotTable(omssubtype="MACROINFORMATION", procname="SPSSINC CREATE DUMMIES",
            tabletitle=_("Macro Definitions"), columnlabels=[_("""Included Variables""")])
        #if not isinstance(root, unicode):
            #uroot = unicode(root, self.myenc)
        #else:
            #uroot = root
        if self.macronames[0]:
            for i, name in enumerate(self.macronames[0]):
                #body = " ".join(self.target[1][i][first:])
                body = self.makenamelist(self.target[1][i])
                spss.SetMacroValue(name, body)
                info.addrow(name, [body])
        if self.macronames[1]:
            #body = " ".join(self.target[2][first:])
            body = self.makenamelist(self.target[2])
            spss.SetMacroValue(self.macronames[1], body)
            info.addrow(self.macronames[1], [body])
        if self.macronames[2]:
            #body = " ".join(self.target[3][first:])
            body = self.makenamelist(self.target[3])
            spss.SetMacroValue(self.macronames[2], body)
            info.addrow(self.macronames[2], [body])
        try:
            info.generate()
        except:
            print "The macro generation table could not be produced"   # nontranslatable

            #if not isinstance(macroname, unicode):
                #macroname = unicode(macroname, self.myenc)
            #info.addrow( _("Macro created: %s") % macroname)
            
    def makenamelist(self, targetlist):
        """Return (possibly empty) string of variable names for macro definition and report
        targetlist is the list of names for the macro before filtering
        
        Removes any poisoned variable in the list if omitfirst"""
        
        if self.omitfirst:
            targetlist = [item for item in targetlist if not item in self.exclude]
            #for i, v in enumerate(targetlist):
                #if not v in self.onlyscale:
                    #targetlist.pop(i)
                    #break
        return " ".join(targetlist)
    
def _safeval(val, quot):
    "return safe value for quoting with quot, which may be single or double quote or blank"
    if quot:
        return val.replace(quot, quot+quot)
    else:
        return val



def Run(args):
    """Execute the CREATE DUMMIES extension command"""

    args = args[args.keys()[0]]

    oobj = Syntax([
        Template("VARIABLE", subc="",  ktype="existingvarlist", var="varname", islist=True),
        Template("VARIABLES", subc="",  ktype="existingvarlist", var="varnames", islist=True),
        Template("ROOTNAME", subc="", ktype="varname", var="root", islist=True),
        Template("ROOTNAME1", subc="", ktype="varname", var="root1", islist=True),
        Template("ROOTNAME2", subc="", ktype="varname", var="root2"),
        Template("ROOTNAME3", subc="", ktype="varname", var="root3"),
        Template("MAXVARS", subc="OPTIONS", ktype="int", var="maxvars"),
        Template("ORDER", subc="OPTIONS", ktype="str", var="order", vallist=['a', 'd']),
        Template("MACRONAME", subc="OPTIONS", ktype="literal", var="macroname", islist=True),
        Template("MACRONAME1", subc="OPTIONS", ktype="literal", var="macroname1", islist=True),
        Template("MACRONAME2", subc="OPTIONS", ktype="literal", var="macroname2"),
        Template("MACRONAME3", subc="OPTIONS", ktype="literal", var="macroname3"),
        Template("OMITFIRST", subc="OPTIONS", ktype="bool", var="omitfirst"),
        Template("USEML", subc="OPTIONS", ktype="bool", var="usemls"),
        Template("USEVALUELABELS", subc="OPTIONS", ktype="bool", var="usevaluelabels"),
        Template("HELP", subc="", ktype="bool")])
    
    #enable localization
    global _
    try:
        _("---")
    except:
        def _(msg):
            return msg
    # A HELP subcommand overrides all else
    if args.has_key("HELP"):
        ###print helptext
        helper()
    else:
        processcmd(oobj, args, CreateBasisVariables, vardict=spssaux.VariableDict())
        
class NonProcPivotTable(object):
    """Accumulate an object that can be turned into a basic pivot table once a procedure state can be established"""
    
    def __init__(self, omssubtype, outlinetitle="", tabletitle="", caption="", rowdim="", coldim="", columnlabels=[],
                 procname="Messages"):
        """omssubtype is the OMS table subtype.
        caption is the table caption.
        tabletitle is the table title.
        columnlabels is a sequence of column labels.
        If columnlabels is empty, this is treated as a one-column table, and the rowlabels are used as the values with
        the label column hidden
        
        procname is the procedure name.  It must not be translated."""
        
        attributesFromDict(locals())
        self.rowlabels = []
        self.columnvalues = []
        self.rowcount = 0

    def addrow(self, rowlabel=None, cvalues=None):
        """Append a row labelled rowlabel to the table and set value(s) from cvalues.
        
        rowlabel is a label for the stub.
        cvalues is a sequence of values with the same number of values are there are columns in the table."""

        if cvalues is None:
            cvalues = []
        self.rowcount += 1
        if rowlabel is None:
            self.rowlabels.append(str(self.rowcount))
        else:
            self.rowlabels.append(rowlabel)
        self.columnvalues.extend(cvalues)
        
    def generate(self):
        """Produce the table assuming that a procedure state is now in effect if it has any rows."""
        
        privateproc = False
        if self.rowcount > 0:
            try:
                table = spss.BasePivotTable(self.tabletitle, self.omssubtype)
            except:
                StartProcedure(_("Create dummy variables"), self.procname)
                privateproc = True
                table = spss.BasePivotTable(self.tabletitle, self.omssubtype)
            if self.caption:
                table.Caption(self.caption)
            if self.columnlabels != []:
                table.SimplePivotTable(self.rowdim, self.rowlabels, self.coldim, self.columnlabels, self.columnvalues)
            else:
                table.Append(spss.Dimension.Place.row,"rowdim",hideName=True,hideLabels=True)
                table.Append(spss.Dimension.Place.column,"coldim",hideName=True,hideLabels=True)
                colcat = spss.CellText.String("Message")
                for r in self.rowlabels:
                    cellr = spss.CellText.String(r)
                    table[(cellr, colcat)] = cellr
            if privateproc:
                spss.EndProcedure()
                
def attributesFromDict(d):
    """build self attributes from a dictionary d."""
    self = d.pop('self')
    for name, value in d.iteritems():
        setattr(self, name, value)

def StartProcedure(procname, omsid):
    """Start a procedure
    
    procname is the name that will appear in the Viewer outline.  It may be translated
    omsid is the OMS procedure identifier and should not be translated.
    
    Statistics versions prior to 19 support only a single term used for both purposes.
    For those versions, the omsid will be use for the procedure name.
    
    While the spss.StartProcedure function accepts the one argument, this function
    requires both."""
    
    try:
        spss.StartProcedure(procname, omsid)
    except TypeError:  #older version
        spss.StartProcedure(omsid)


def helper():
    """open html help in default browser window
    
    The location is computed from the current module name"""
    
    import webbrowser, os.path
    
    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "markdown.html"
    
    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print("Help file not found:" + helpspec)
try:    #override
    from extension import helper
except:
    pass    

#!/usr/bin/python 
import cgi
import math
import csv
import StringIO
import sys
import cgitb # these two lines give detailed error reports through HTML - comment out for production
cgitb.enable()
import BIL


#error handling - spit out HTML file with error message
def errorout(msg):
    print 'Content-type: text/html\n'
    print "<H1>",msg,"</H1>"
    quit()
    


# ----------------------
# - the fetch routines -
# ----------------------
#
# -- latlon2env --
def latlon2env(lat,lon):
    #print "<br>env=",BIL.lookupBIL(r'c:\data\worldclim\tmin4',lat,lon),"<br>"
    #print "lat[1]=",lat[1]," lon[0]=",lon[0]
    MAT=BIL.lookupBIL(r'./worldclim/bio1',lat,lon)
    TSD=BIL.lookupBIL(r'./worldclim/bio4',lat,lon)
    AnnTMin=BIL.lookupBIL(r'./worldclim/bio6',lat,lon)
    ANNPREC=BIL.lookupBIL(r'./worldclim/bio12',lat,lon)
    return [MAT,TSD,AnnTMin,ANNPREC],['MAT (C*10)','Tsd (C*100)','AnnTMin (C*10)','AnnPrecip (mm)']

# -- latlon2spec --
def latlon2spec(lat,lon):
    print "lat[1]=",lat[1]," lon[0]=",lon[0]

# -- spec2range --
def lspec2range(specs):
    print "specs[1]=",specs(1)

# -- spec2valid --
def lspec2valid(specs):
    print "specs[1]=",specs(1)

# ------------------------------
# - the CGI processing routine -
# ------------------------------
form=cgi.FieldStorage()
if "get" not in form or "from" not in form:
    errorout("Error - please provide get and from fields in query")
# required opening of CGI scripts with HTML output:
gv=form.getvalue("get")
fv=form.getvalue("from")
mapval=form.getvalue("map")
#print "get=",form.getvalue("get"),"<p>"
#print "from=",form.getvalue("from"),"<p>"
lats=[];lons=[];binomials=[]
if fv=="latlon":
    #
    #load lat lon
    #
    if "shape" not in form:
        shp="point"
    else:
        shp=form.getvalue("shape")
    if shp!="point" and shp!="points" and shp!="poly" and shp!="polygon":
        errorout("Error - invalid shape for latlons: '"+shp)
    else: #clean up accepted synonyms
    	if shp=="points":
    	    shp="point"
    	elif shp=="polygon":
    	    shp="poly"
    #process this case
    if "latlons" in form:
        fileitem=form["latlons"]
        txt=fileitem.file.read()
    else:
    	txt=""
    if txt!="": #have non-empty uploaded file, ignore direct input
        #print "txt='",txt,"'"
	f=StringIO.StringIO(txt)
	ll = csv.reader(f,delimiter=",")
	for row in ll:
	    lats.append(row[0])
	    lons.append(row[1])
	lats=[float(i) for i in lats]
	lons=[float(i) for i in lons]
	#print "lats=",lats
    elif "lat" in form and "lon" in form and form["lat"].value!="" and form["lon"].value!="":
        #.replace('\n',',')???
        lats=[float(i) for i in form["lat"].value.replace('\n',',').split(",")]
        lons=[float(i) for i in form["lon"].value.replace('\n',',').split(",")]
    else:
        errorout("Error - must provide 'lat' and 'lon' fields (or 'latlons')")
    #print "lats[0]=",lats[0],";   lons[1]=",lons[1],";   shape=",shp,"<p>"
    #
    #process to the transformation
    #
    if gv=="env" or gv=="environ" or gv=="environment":
        #print "Content-type: text/html\n\nGetting environment from latlon"
        dat,labels=latlon2env(lats,lons)
    elif gv=="species":
        print "Content-type: text/html\n\nGetting species from latlon"
        out=latlon2spec(lats,lons)
    elif gv=="field" or gv=="user":
        print "Content-type: text/html\n\nGetting user field from latlon"
    else:
        errorout("Error - unrecognized get value for from=latlon: '"+gv+"'")
elif fv=="species":
    #
    #load species binomials
    #
    if "specs" in form: #file upload
        fileitem=form["specs"]
        txt=fileitem.file.read()
    else:
    	txt=""
    if txt!="": #have non-empty uploaded file, ignore direct input
        binomials=txt.replace('\n',',').replace('\r','').split(',')
    elif "spec" in form and form["spec"]!="":
        binomials=form["spec"].value.replace('\n',',').replace('\r','').split(",")
    else:
        errorout("Error - must provide species binomials")
    #print binomials,"<p>"
    #
    #process to the transformation
    #
    if gv=="range" or gv=="ranges":
        print "Content-type: text/html\n\nGetting ranges from species names"
        out=spec2range(binomials)
    elif gv=="valid" or gv=="validation":
        print "Content-type: text/html\n\nValidating species binomials"
        out=spec2valid(binomials)
    elif gv=="trait" or gv=="traits":
        print "Content-type: text/html\n\nGetting traits from species names"
    elif gv=="phyl" or gv=="phylogeny":
        print "Content-type: text/html\n\nGetting phlogeny from species names"
    else:
        errorout("Error - unrecognized get value for from=species: '"+gv+"'")
        quit()
else:
    errorout("Error - unrecognized from value "+fv)
    quit()


#OK - success so far! print out CSV file
# If the want to se it on a map
if mapval=="yes":
        print "Showing you map for it"
        writer=csv.writer(sys.stdout,dialect='excel')
        for r in zip(lats,lons,*dat):  #might need map with NONE for ragged arrays??
            writer.writerow(r)

else:
    quit()


print 'Content-type: application/vnd.ms-excel\nContent-Disposition: attachment; filename=iPlantGEO.csv;\n'
writer=csv.writer(sys.stdout,dialect='excel')
if fv=="latlon":
    writer.writerow(['Lat','Lon']+labels)
    for r in zip(lats,lons,*dat):  #might need map with NONE for ragged arrays??
        writer.writerow(r)
elif fv=="species":
    writer.writerow(labels)
    for r in zip(binomials,*ary):
        writer.writerow(r)

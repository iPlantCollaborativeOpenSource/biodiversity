def readBILheader(fbase):
     hdr={};
     fh=open(fbase+'.hdr', "r")
     try:
          for line in fh:
               res=line.split()
               if res: #looks like pair - use it
                    hdr[res[0]]=res[1]
     finally:
          fh.close()
     return hdr

def lookup1BIL(fh,offset):
     import struct
     fh.seek(offset*2)
     (i,)=struct.unpack('h',fh.read(2))
     return i;

def lookupBIL(fbase,lats,lons):
     hdr=readBILheader(fbase)
     if hdr["Projection"]!="GEOGRAPHIC" or int(hdr["NBITS"])!=16:
          print "Error: only works on integer geographic BIL files (Proj=",hdr["Projection"],"bits=",hdr["NBITS"]
          quit()
     deltax=float(hdr["XDIM"])
     deltay=float(hdr["YDIM"])
     leftedge=float(hdr["ULXMAP"])-deltax/2
     topedge=float(hdr["ULYMAP"])+deltay/2
     nrows=int(hdr["NROWS"])
     ncols=int(hdr["NCOLS"])
     #rowsize=int(hdr["TOTALROWBYTES"])
     nodata=int(hdr["NODATA"])
     env=[]
     fh=open(fbase+'.bil','rb')
     for la,lo in zip(lats,lons):
          col=int(round((lo-leftedge)/deltax))
          row=int(round((topedge-la)/deltax))
          offset=row*ncols+col
          #print "offset=",offset
          result=lookup1BIL(fh,offset)
          if result==nodata: result=float('nan')
          env.append(result)
     fh.close()
     return env
          
     
    
if __name__ == '__main__':
     #hdr=readBILheader(r'c:\data\worldclim\tmin9')
     #print hdr
     #env=lookupBIL(r'c:\data\worldclim\tmin4',[-60,0,60,90],[90,90,90,90])
     env=lookupBIL(r'./worldclim/tmin4',[-40,10,20,25,30,35,40],[
          -100,-100,-100,-100,-100,-100,-100])
     print "env=",env
     #correct answer for tmin4 is:  NaN,NaN, 6.6, 12.4,11.6,7.9,2.3
     #as verified in matlab (although with lon=-99.9999, lon=100 takes pixel to left

    

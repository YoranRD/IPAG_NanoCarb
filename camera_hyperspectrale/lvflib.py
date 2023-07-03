# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 11:05:20 2022

@author: S. Gousset, Y. Bourdin, A. Roussel, (R. Garnier)
"""

#import cv2
import numpy as np
from scipy.interpolate import interp1d, interp2d, CloughTocher2DInterpolator
from scipy.ndimage import sobel
from scipy.signal import correlate2d
import scipy.constants as cst
import cv2
#import scipy.optimize as so
from astropy.io import fits
import matplotlib as matplot
import glob
import scipy.optimize as so 
# import plotly.express as px

class ImSPOCFitsClass:
    """
    Load and manage .fits files containing data acquired with ImSPOC-like imaging spectrometer. Automaticaly create a ImSPOCDataCLass object. 
    S. Gousset from Y. Bourdin 2021
    
    attributes:
    
    method:
    
    usage examples:
        
    """
    
    def __init__(self,path,spectraltag=None,timestamptag=None,powertag=None,_startpix=[48,48],exten_no_start=1,winsize=[96,96]): #,hdul_object=None
        '''
        

        Parameters
        ----------
        path : TYPE
            DESCRIPTION.
        spectraltag : TYPE, optional
            DESCRIPTION. The default is None.
        timestamptag : TYPE, optional
            DESCRIPTION. The default is None.
        powertag : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        '''
        self.fits = fits.open(path)
        #if hdul_object is None:
        #    print('READING FITS FROM FILE')
        #    self.fits = fits.open(path)
        #else:
        #    print('INSTANCIATING HDUL OBJECT')
        #    self.fits = hdul_object
        #self.fits_list = [self.fits]
        #self.primary = self.fits[0]
        
        self.images = []
        for i in range (exten_no_start, len(self.fits)):
            # self.images.append(self.fits[i].data) # création d'objet ImSPOCDataClass pour chaque image
            self.images.append(ImSPOCDataClass(self.fits[i].data,self.fits[i].header,centre=None,mapisrf=None, mskval=None, mskthumbnail=None,_startpix=_startpix,winsize=winsize)) # thumbsize=None,thumbpitch=None,startpix=None création d'objet ImSPOCDataClass pour chaque image
        
        if spectraltag is not None:
            self.spectralscale = []
            for i in range (1, len(self.fits)):     # parcours les fichiers de scan
                self.spectralscale.append( float(self.fits[i].header[spectraltag]) ) 
            #self.spectralscale=np.zeros(len(self.fits))
            #for i in range (1, len(self.fits)):
            #    self.spectralscale[i]=float(self.fits[i].header[spectraltag])
        else:
            self.spectralscale = []

        if timestamptag is not None:
            print('/!\ TIMESTAMP MANAGEMENT NOT YET IMPLEMENTED')
            self.timestamp = []
            for i in range (1, len(self.fits)):     # parcours les fichiers de scan
                self.timestamp.append( float(self.fits[i].header[timestamptag]) ) 
        else:
            self.timestamp = []

        if powertag is not None:
            print('/!\ POWER MANAGEMENT NOT YET IMPLEMENTED')
            self.powervalue = []
            for i in range (1, len(self.fits)):     # parcours les fichiers de scan
                self.powervalue.append( float(self.fits[i].header[powertag]) ) 
        else:
            self.powervalue = []

    def merge(self, ImSPOCFitsClass_inst):
        '''
        ImSPOCFitsClass method to merge another ImSPOCFitsClass instance into self instance. ; from Y. Bourdin 2021 ImSPOC.py

        Parameters
        ----------
        ImSPOCFitsClass_inst : ImSPOCFitsClass
            ImSPOCFitsClass instance to be merged with self.

        Returns
        -------
        None.

        '''
        assert type(ImSPOCFitsClass_inst)==type(self)
        #if self.primary.header != ImSPOCFitsClass_inst.primary.header:
        #    print('Warning: merging fits with different primary headers')
        self.images = self.images + ImSPOCFitsClass_inst.images
        #self.fits_list.append(ImSPOCFitsClass_inst.fits_list) # /!\ PROBLEME SUR LA LISTE MERGEE
        # self.fits_list = self.fits_list + ImSPOCFitsClass_inst.fits_list
        self.fits = self.fits + ImSPOCFitsClass_inst.fits

        self.spectralscale = self.spectralscale + ImSPOCFitsClass_inst.spectralscale
        self.timestamp = self.timestamp + ImSPOCFitsClass_inst.timestamp
        self.powervalue = self.powervalue + ImSPOCFitsClass_inst.powervalue        
        
    def apply_coefnorm(self,coef_norm):
        '''
        Normalize monochromatic scan sequence of data by photon rate  

        Parameters
        ----------
        coef_norm : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        for i in range (0, np.size(self.images)):
            temp=self.images[i].data
            temp=np.float_(temp)
            self.images[i].data=temp/coef_norm[i]

    def get_3dval(self,coord):
        '''
        Return temporal time sequence (or spectral scan) for a single pixel coord[0];coord[1] or a list of pixel

        Parameters
        ----------
        coord : list [[x,y],[...],...]
            DESCRIPTION.

        Returns
        -------
        value : TYPE
            DESCRIPTION.

        '''
        
        # value=np.zeros(np.size(self.images))
        list_value=[]
        for l in range(0,len(coord)):
            # print(l,coord[l][0],coord[l][1])
            value=np.zeros(np.size(self.images))
            for n in range (0, np.size(self.images)):
                value[n]=self.images[n].data[coord[l][1],coord[l][0]] # /?\ CHECK INDICE X Y OU Y X => OK
            list_value.append(value)
            
        return list_value

    def get_med(self,msk=None):
        '''
        Estimation of median value given msk

        Parameters
        ----------
        msk : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        med : TYPE, optional
            DESCRIPTION. The default is None.

        '''
        if msk is not None:
            print('get_med: /!\ MASKED ARRAY NOT IMPLEMENTED')
            # TODO > import numpy.ma as ma y = ma.array([1, 2, 3], mask = [0, 1,  
        
        med=np.zeros(np.size(self.images))
        for n in range (0, np.size(self.images)):
            med[n]=np.median(self.images[n].data)
        
        return med

    def corr_darkdrift(self,val):
        '''
        Correction of temporal/or spectral dark drift

        Parameters
        ----------
        val : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        for n in range (0, np.size(self.images)):
            self.images[n].data-=val[n]
        
    # def set_dark(self):
    #     print('toto')    
    
    # def make_tempmed(self):
    #     print('toto')
    
       
class ImSPOCDataClass:
    """
    Type for acquisition from ImSPOC
    
    attributes:
   
    method:
    
    usage examples:
        
    """
    def __init__(self,data,header,thumbsize=[64,64],thumbpitch=[64,64],winsize=[64,64],_startpix=[32,32],thumbref=40,centre=None,mapfov=None,mapisrf=None, mskval=None, mskthumbnail=None):
        '''
        

        Parameters
        ----------
        data : TYPE
            DESCRIPTION.
        header : TYPE
            DESCRIPTION.
        thumbsize : TYPE, optional
            DESCRIPTION. The default is [96,96].
        thumbpitch : TYPE, optional
            DESCRIPTION. The default is [96,96].
        _startpix : TYPE, optional
            DESCRIPTION. The default is [48,48].
        centre : TYPE, optional
            DESCRIPTION. The default is None.
        mapisrf : TYPE, optional
            DESCRIPTION. The default is None.
        mskval : TYPE, optional
            DESCRIPTION. The default is None.
        mskthumbnail : TYPE, optional
            DESCRIPTION. The default is None.

        A -x- DEFINITION/CHARGEMENT CENTRE DES IMAGETTES
        B -x- DECOUPAGE MASQUE DES IMAGETTES AUTOUR DU CENTRE
        C -x- (DEFINITION/CHARGEMENT MASQUE DE VALIDITE 2D A PRIORI)
        D -x- DEFINITION/CHARGEMENT MAP DE DEPLACEMENT PIXELLIQUE
        E -x- RECALAGE DES IMAGETTES SUIVANT ORDRE TABCENTRES ET MAP DE DEPLACEMENT
        F -x- 
        G -x- 
        H -x- 
        I -x- 
        J -x- 

        Returns
        -------
        None.

        '''
        self.data=data
        self.header=header
        
        self.thumbsize = thumbsize
        self.thumbpitch = thumbpitch
        self.winsize = winsize
        self.thumbref = thumbref
        self.startpix=_startpix
        # TODO passer startpix en variable locale uniquement => NON !?
        # self.startpix = startpix
        
        # Thumbnails center 
        if centre is not None:
            self.centre = centre
        else:
            # Masque géométrique par défaut /!\ TODO optimiser avec meme masque pour tous les fichiers de la meme serie
            _nthumby=np.fix(np.size(self.data,axis=0)/self.thumbpitch[0])
            _nthumbx=np.fix(np.size(self.data,axis=1)/self.thumbpitch[1])
            _nthumbt=int(_nthumbx*_nthumby)
            self.nthumbt=int(_nthumbx*_nthumby) # /!\ SALE
            #print('DEBUG',_nthumbt,self.nthumbt)
            _startpix_0=np.array([_startpix[0]-np.fix(_startpix[0]/self.thumbpitch[0])*self.thumbpitch[0],_startpix[1]-np.fix(_startpix[1]/self.thumbpitch[1])*self.thumbpitch[1]])
            self.centre = np.zeros((_nthumbt,2),dtype=int)
            count=0
            for x in range(0,int(_nthumbx)): # /?\ CHECK INDICE X Y OU Y X
                for y in range(0,int(_nthumby)):
                    self.centre[count,:]=[_startpix_0[0]+x*self.thumbpitch[0],_startpix_0[1]+y*self.thumbpitch[1]]
                    count+=1
        
        # . Defining crop table coordinates 
        tabx_start=np.zeros(_nthumbt,dtype=int)
        tabx_end=np.zeros(_nthumbt,dtype=int)
        taby_start=np.zeros(_nthumbt,dtype=int)
        taby_end=np.zeros(_nthumbt,dtype=int)
        for t in range(0,_nthumbt):
            if self.centre[t,1]-int(self.thumbsize[1]/2) < 0:
                tabx_start[t]=0
            else:
                tabx_start[t]=int(self.centre[t,1]-int(self.thumbsize[1]/2) )
            if self.centre[t,1]+int(self.thumbsize[1]/2) > np.size(self.data,axis=0)-1:
                tabx_end[t]=int(np.size(self.data,axis=0)-1 )
            else:
                tabx_end[t]=np.fix(self.centre[t,1]+int(self.thumbsize[1]/2) )
            if self.centre[t,0]-int(self.thumbsize[0]/2) < 0:
                taby_start[t]=0
            else:
                taby_start[t]=int(self.centre[t,0]-int(self.thumbsize[0]/2) )
            if self.centre[t,0]+int(self.thumbsize[0]/2) > np.size(self.data,axis=1)-1:
                taby_end[t]=np.size(self.data,axis=1)-1
            else:
                taby_end[t]=int(self.centre[t,0]+int(self.thumbsize[0]/2) )       
            #print('DEBUG',t,tabx_start[t],tabx_end[t],taby_start[t],taby_end[t])
            
        # Thumbnails mask np.array[int(xs,ys,nthumbt)]
        if mskthumbnail is not None and centre is not None:
            self.mskthumbnail = mskthumbnail
        else:
            # self.mskthumbnail = 'Default Thumbnails mask not yet implemented'
            self.mskthumbnail=np.zeros((np.size(self.data,axis=0),np.size(self.data,axis=1)),dtype=int)
            for t in range(0,_nthumbt):
                #self.mskthumbnail[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ]=t+1
                self.mskthumbnail[ tabx_start[t]:tabx_end[t], taby_start[t]:taby_end[t] ]=t+1
                
        # Mask of validity
        if mskval is not None:
            self.mskval = mskval
        else:
            self.mskval = np.zeros((np.size(self.data,axis=0),np.size(self.data,axis=1)),dtype=bool)
            for t in range(0,_nthumbt):
                #self.mskval[ self.centre[t,1]-int(self.winsize[1]/2):self.centre[t,1]+int(self.winsize[1]/2), self.centre[t,0]-int(self.winsize[0]/2):self.centre[t,0]+int(self.winsize[0]/2) ]=True
                self.mskval[ tabx_start[t]:tabx_end[t], taby_start[t]:taby_end[t] ]=True
    
        # . Pixel to Fov Map and guess registration
        _x=np.arange(self.thumbsize[0])-(self.thumbsize[0]/2)
        _y=np.arange(self.thumbsize[1])-(self.thumbsize[1]/2)
        _xx, _yy = np.meshgrid(_x, _y)
        #print('DEBUG',np.shape(_xx),np.shape(_yy))
        #print('DEBUG',np.shape(self.centre))
        if mapfov is not None:
            self.mapfov=mapfov 
            # . Registration by interpolation
            self.data_3D=self.make_thumb_registration(self)
        else:
            self.data_3D=np.zeros((self.thumbsize[0],self.thumbsize[1],_nthumbt))
            self.mapfov=np.zeros((np.size(self.data,axis=0),np.size(self.data,axis=1),2),dtype=int)
            for t in range(0,_nthumbt):
                #print('DEBUG',t,self.centre[t,1]-int(self.thumbsize[1]/2),self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2),self.centre[t,0]+int(self.thumbsize[0]/2))
                #self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,0]=_xx
                self.mapfov[ tabx_start[t]:tabx_end[t], taby_start[t]:taby_end[t] ,0]=_xx
                #self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,1]=_yy
                self.mapfov[ tabx_start[t]:tabx_end[t], taby_start[t]:taby_end[t] ,1]=_yy
            # . Registration by simple thumbnail cropping 
            for t in range(0,_nthumbt):
                #print('DEBUG THUMB RECO ',t,end='\r',flush=True)
                #self.data_3D[:,:,t]=self.data[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2)]
                self.data_3D[:,:,t]=self.data[ tabx_start[t]:tabx_end[t], taby_start[t]:taby_end[t] ]
    
    def set_mskval(self,winsize=[96,96]):
        self.winsize=winsize
        self.mskval = np.zeros((np.size(self.data,axis=0),np.size(self.data,axis=1)),dtype=int)
        for t in range(0,self.nthumbt):
            # /?\ /?\ /?\ /?\ /?\ /?\ /?\ /?\ /?\ /?\ /?\ /?\
            self.mskval[ self.centre[t,1]-int(self.winsize[1]/2):self.centre[t,1]+int(self.winsize[1]/2), self.centre[t,0]-int(self.winsize[0]/2):self.centre[t,0]+int(self.winsize[0]/2) ]=1

    def set_centre(self,centre=None):
        # /!\ /!\ /!\ /!\ ATTENTION AU INDICE X Y  ===> OK
        print('DEV set_centre not tested')
        if centre is not None:
            centre=np.round(centre)
            centre=np.int_(centre)
            self.centre=centre
        else:
            _nthumby=np.fix(np.size(self.data,axis=0)/self.thumbpitch[0])
            _nthumbx=np.fix(np.size(self.data,axis=1)/self.thumbpitch[1])
            _startpix_0=np.array([self.startpix[0]-np.fix(self.startpix[0]/self.thumbpitch[0])*self.thumbpitch[0],self.startpix[1]-np.fix(self.startpix[1]/self.thumbpitch[1])*self.thumbpitch[1]])
            self.centre = np.zeros((self.nthumbt,2),dtype=int)
            count=0
            for x in range(0,int(_nthumbx)): # /?\ CHECK INDICE X Y OU Y X
                for y in range(0,int(_nthumby)):
                    # /!\ /!\ /!\ /!\ ATTENTION AU INDICE X Y ===> OK
                    self.centre[count,:]=[_startpix_0[0]+x*self.thumbpitch[0],_startpix_0[1]+y*self.thumbpitch[1]]
                    count+=1
            
        self.set_mskthumbnail(mskthumbnail=None) # =>

    def set_mskthumbnail(self,mskthumbnail=None):
        print('DEV set_mskthumbnail not tested')
        if mskthumbnail is not None:
            self.mskthumbnail=mskthumbnail
        else:
            self.mskthumbnail=np.zeros((np.size(self.data,axis=0),np.size(self.data,axis=1)),dtype=int)
            for t in range(0,self.nthumbt):
                #print('DEBUG',t,self.centre[t,1]-int(self.thumbsize[1]/2),self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2),self.centre[t,0]+int(self.thumbsize[0]/2))
                self.mskthumbnail[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ]=t+1
        
        self.set_mapfov(mapfov=None)
    
    def set_mapfov(self,mapfov=None):
        print('DEV set_mapfov not tested')
        if mapfov is not None:
            self.mapfov=mapfov
        else:
            _x=np.arange(self.thumbsize[0])-(self.thumbsize[0]/2)
            _y=np.arange(self.thumbsize[1])-(self.thumbsize[1]/2)
            _xx, _yy = np.meshgrid(_x, _y)
            self.mapfov=np.zeros((np.size(self.data,axis=0),np.size(self.data,axis=1),2),dtype=int)
            for t in range(0,self.nthumbt):
                self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,0]=_xx
                self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,1]=_yy
        
        self.extract_thumbnail()

    def extract_thumbnail(self):
        print('DEV extract_thumbnail not tested')
        self.data_3D=np.zeros((self.thumbsize[0],self.thumbsize[1],self.nthumbt))
        # . Registration by simple thumbnail cropping 
        for t in range(0,self.nthumbt):
            #print('DEBUG THUMB RECO ',t,end='\r',flush=True)
            self.data_3D[:,:,t]=self.data[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2)]

    def make_thumb_registration(self):
        print('DEV make_thumb_registration not tested')
        # Thumbnails co registration whitin mapfov => CloughTocher2DInterpolator
        # . Reference coordinates (from reference thumbnail)
        _xref=self.mapfov[ self.centre[self.thumbref,1]-int(self.thumbsize[1]/2):self.centre[self.thumbref,1]+int(self.thumbsize[1]/2), self.centre[self.thumbref,0]-int(self.thumbsize[0]/2):self.centre[self.thumbref,0]+int(self.thumbsize[0]/2) ,0]
        _yref=self.mapfov[ self.centre[self.thumbref,1]-int(self.thumbsize[1]/2):self.centre[self.thumbref,1]+int(self.thumbsize[1]/2), self.centre[self.thumbref,0]-int(self.thumbsize[0]/2):self.centre[self.thumbref,0]+int(self.thumbsize[0]/2) ,1]
        # . 1D reshaping
        _xref1d=np.reshape(_xref,(self.thumbsize[0]*self.thumbsize[1]))
        _yref1d=np.reshape(_yref,(self.thumbsize[0]*self.thumbsize[1]))
        for t in range(0,self.nthumbt):
            print('DEBUG THUMB RECO ',t,end='\r',flush=True)
            # . x-displacement thumbnail map extraction
            _x=self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,0]
            # . y-displacement thumbnail map extraction
            _y=self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,1]
            # . Intensity extraction
            _z=self.data[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2)]
            # . 1D reshaping
            _x1d=np.reshape(_x,(self.thumbsize[0]*self.thumbsize[1]))
            _y1d=np.reshape(_y,(self.thumbsize[0]*self.thumbsize[1]))
            _z1d=np.reshape(_z,(self.thumbsize[0]*self.thumbsize[1]))
            # . /?\ returning interp object ?
            _interp = CloughTocher2DInterpolator(list(zip(_x1d, _y1d)), _z1d,fill_value=0)
            # . interpolating
            _znew1d=_interp(list(zip(_xref1d,_yref1d)))   
            _znew=np.reshape(_znew1d,(self.thumbsize[0],self.thumbsize[1]))
            self.data_3D[:,:,t]=_znew

    def set_subpixtranslation(self,pix_displ):
        print('DEV set_subpixtranslation not tested')
        # . mapfov modification
        for t in range(0,self.nthumbt):
            _courantX=self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,0]
            _courantY=self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,1]
            _courantX=_courantX-pix_displ[t,0]
            _courantY=_courantY-pix_displ[t,1]
            self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,0]=_courantX
            self.mapfov[ self.centre[t,1]-int(self.thumbsize[1]/2):self.centre[t,1]+int(self.thumbsize[1]/2), self.centre[t,0]-int(self.thumbsize[0]/2):self.centre[t,0]+int(self.thumbsize[0]/2) ,1]=_courantY
        
        self.make_thumb_registration()

def readfitscube_frommultifile(path,filebasename,spectraltag=None,_startpix=[48,48],winsize=[96,96],exten_no_start=1):
    '''
    Read several .fits data cubes and merge them into a single ImSPOCDataFits instance

    Parameters
    ----------
    path : str
        Directory path without final '/'.
    filebasename : str
        File base name to search in path.

    Returns
    -------
    imspocinst : ImSPOCFitsClass
        ImSPOCFitsClass instance with concatenated read data.

    '''
    list_file=glob.glob(path+'/*'+filebasename+'*.fits')
#   list_file=glob.glob(path+'/*'+filebasename+'_*.fits')

    for i in range(0,len(list_file)): # on merge les fichiers du scan Zolix
        print('Reading fits files >',i,'/',len(list_file)-1,list_file[i])
        temp_inst=ImSPOCFitsClass(list_file[i],spectraltag=spectraltag,_startpix=_startpix,winsize=winsize,exten_no_start=exten_no_start)
        if i == 0:
            imspocinst=temp_inst
        if i > 0:
            imspocinst.merge(temp_inst)
        temp_inst=0
        print('Reading fits files > finish')
    
    return imspocinst

def readandproc_pm101(path_data,filebasename_data,calib_path='',plottoscreen=False,comchar='#',verb=True):
    '''
    Read multiple acquisitions from powermeter PM101, compute average, then convert into photon flow

    Parameters
    ----------
    path_data : str
        Data from PM101 directory path.
    filebasename_data : str
        Data file base name to search in path_data.
    calib_path : str, optional
        Full path of photodiode calibration file. 
    plottoscreen : Boolean, optional
        Plot read data. The default is False.
    comchar : str, optional
        Comment character in read files. The default is '#'.
    verb : Boolean, optional
        Verbose. The default is True.
        
    Returns
    -------
    photonflow_out : scipy.interpolate.interp1d object defined over local variable "wvl"
        Photon flow over scan wavelength scale.

    '''
    list_file=glob.glob(path_data+'/*'+filebasename_data+'*.txt')
    
    if plottoscreen:
        fig, (ax1,ax2,ax3) = matplot.pyplot.subplots(3,1,figsize=(8, 8))#,figsize=(8, 6)
        fig.subplots_adjust(hspace=0.3)
        ax1.set_xlabel('$\lambda$ [nm]')
        ax1.set_ylabel('Current [A]')

    nb_scan=0.
    for i in range(0,len(list_file)):
        if verb:
            print(i,list_file[i])
        temp_data=np.loadtxt(list_file[i],comments=comchar) #,delimiter=None
        if i == 0:
            wvl=temp_data[:,0]    
            current_powermeter=temp_data[:,1]
            nb_scan+=1
        if i > 0:
            if np.sum(temp_data[:,0]-wvl) != 0.:
                raise Exception('PM101 : wavelength scale not equivalent between files')
            current_powermeter+=temp_data[:,1]
            nb_scan+=1
        
        if plottoscreen:
            ax1.plot(temp_data[:,0],temp_data[:,1],label=str(i))    
        temp_data=0
        
    current_powermeter/=nb_scan # [A]
    
    pm_calibdata=np.loadtxt(calib_path,comments='#')
    eta_func=interp1d(pm_calibdata[:,0], pm_calibdata[:,1], kind='linear', bounds_error=None, fill_value=0., assume_sorted=False)
    eta_interp=eta_func(wvl) # interpolation of calibration data over acquisition wavelength scale
    
    power_powermeter=current_powermeter/eta_interp # [W]
    
    photonflow=power_powermeter*(wvl*1e-9)/(cst.Planck*cst.c) # [photon/s]
    
    if plottoscreen:
        ax1.plot(wvl,current_powermeter,color='black',label='mean') 
        # ax2.plot(pm_calibdata[:,0], pm_calibdata[:,1])
        # ax2.plot(wvl,eta_interp) 
        # ax2.set_xlabel('$\lambda$ [nm]')
        # ax2.set_ylabel('$\eta$ [A/W]')
        ax2.plot(wvl,power_powermeter) 
        ax2.set_xlabel('$\lambda$ [nm]')
        ax2.set_ylabel('Optical power [W]')
        ax3.plot(wvl,photonflow) 
        ax3.set_xlabel('$\lambda$ [nm]')
        ax3.set_ylabel('Photon flow [ph.s$^{-1}$]')
        # matplot.pyplot.show()

    photonflow_out=interp1d(wvl, photonflow, kind='linear', bounds_error=None, fill_value=0., assume_sorted=False)

    return photonflow_out

def total_thresholded(lvfSpectraInst,thres_std=3.):
    '''
    

    Parameters
    ----------
    lvfSpectraInst : TYPE
        DESCRIPTION.
    thres_std : TYPE, optional
        DESCRIPTION. The default is 3..

    Returns
    -------
    imtot : TYPE
        DESCRIPTION.

    '''
    
    xs=np.size(lvfSpectraInst.images[0].data,axis=0)
    ys=np.size(lvfSpectraInst.images[0].data,axis=1)
    imtot=np.zeros((xs,ys))
    for j in range (0,ys):
        print('Total seuillé > ',j,' / ',ys-1,end='\r',flush=True)
        for i in range(0,xs):
            if lvfSpectraInst.images[0].mskval[i,j] ==1:
                courant=lvfSpectraInst.get_3dval([[j,i]])
                courant=np.array(courant)
                courant=np.reshape(courant,np.shape(courant)[1])
                courant_tresh=np.zeros(np.shape(courant))
                courant_tresh[courant > np.median(courant)+thres_std*np.std(courant)]=courant[courant > np.median(courant)+thres_std*np.std(courant)]
                imtot[i,j]=np.sum(courant_tresh)
    
    return imtot

def extract_3dmed(cube_in,coord,win_s):
    '''
    

    Parameters
    ----------
    cube_in : TYPE
        Image date cube.
    coord : TYPE
        Coordinate of the FoV point to be extracted. /!\ coord[0] = X coord[1] = Y
    win_s : TYPE
        DESCRIPTION.

    Returns
    -------
    medarray : TYPE
        DESCRIPTION.

    '''
    nim=np.size(cube_in,axis=2)
    medarray=np.zeros(nim)
    for n in range(0,nim):
        medarray[n]=np.median(cube_in[int(coord[1]-win_s/2):int(coord[1]+win_s/2),int(coord[0]-win_s/2):int(coord[0]+win_s/2),n],axis=(0,1))
    
    return medarray

def fitlvf_isrf(lvfSpectraInst,msk=None,savestate=False,reco=False,reco_jstart=0,filepath=''):
    '''
    

    Parameters
    ----------
    lvfSpectraInst : TYPE
        DESCRIPTION.
    msk : TYPE, optional
        DESCRIPTION. The default is None.
    savestate : TYPE, optional
        DESCRIPTION. The default is False.
    reco : TYPE, optional
        DESCRIPTION. The default is False.
    reco_jstart : TYPE, optional
        DESCRIPTION. The default is 0.
    filepath : TYPE, optional
        DESCRIPTION. The default is ''.

    Returns
    -------
    mapcoef_fit : TYPE
        DESCRIPTION.
    mapfailure : TYPE
        DESCRIPTION.

    '''
    if msk is None:
        msk=lvfSpectraInst.images[0].mskval
    
    xs=np.size(lvfSpectraInst.images[0].data,axis=0)
    ys=np.size(lvfSpectraInst.images[0].data,axis=1)
    
    if reco:
        print('ISRF MAP RECO, loading:'+filepath+'.npy')
        print('ISRF MAP RECO, restarting at j= '+str(reco_jstart))
        mapcoef_fit=np.load(filepath+'.npy')
    else:    
        mapcoef_fit=np.zeros((xs,ys,5))
    
    mapfailure=np.zeros((xs,ys))
    
    for j in range(reco_jstart,ys):
        print('ISRF Fitting > ',j,' / ',ys-1,end='\r',flush=True)
        if savestate:
            np.save(filepath, mapcoef_fit)
        for i in range(0,xs):
            if msk[i,j] == 1:
                
                #print('ISRF Fitting > ',i,' / ',xs-1,' - ',j,' / ',ys-1,end='\r',flush=True)
                
                courant=lvfSpectraInst.get_3dval([[j,i]])
                courant=np.reshape(courant,np.size(courant))
                
                ind_fwhm=np.where(courant >= 0.5*np.max(courant))
                try:
                    fwhm_guess=(lvfSpectraInst.spectralscale[ind_fwhm[0][-1]]-lvfSpectraInst.spectralscale[ind_fwhm[0][0]])/(2.*np.sqrt(2.*np.log(2)))
                    l0_guess=lvfSpectraInst.spectralscale[np.where(courant == np.max(courant))[0][0]]
                    initguess=(np.max(courant),fwhm_guess,l0_guess,0.,0.) 
                    
                    # . Fit
                    # TODO 2023 02 13 => GESTION DES EXEPTION
                    try :
                        constants,covariance = so.curve_fit(anafct_gaussian , lvfSpectraInst.spectralscale , courant , p0=initguess,method='trf')
                        mapcoef_fit[i,j,:]=constants
                    except :
                        #print('Failure: ',i,j)
                        mapfailure[i,j]=1
                except :
                    mapfailure[i,j]=1
                    
    return mapcoef_fit, mapfailure

def anafct_gaussian(xdata,heigth,sig0,lambda0,pol0,pol1):#,pol=(0,0)
     
    ydata=np.zeros(len(xdata))
    for i in range(0,len(xdata)):
        #ydata[i] = heigth * np.exp(-0.5 * ((xdata[i] - lambda0)/sig0)**2) #+ pol[0] + pol[1]*xdata
        ydata[i] = heigth * np.exp( -((xdata[i] - lambda0)**2)/(2.*sig0**2) ) + pol0 + pol1*xdata[i]
    
    return ydata

def preprocess_data(path_science,filebase_science,path_dark=None,filebase_dark=None,exten_no_start=1,SubRow_science=None, SubRow_dark=None):
    '''
    #1a met en memoire tous les fichiers fits "science" d'une liste x
    #1b met en memoire tous les fichiers fits "fond" d'une liste x
    #2a mediane/moyenne tempo pix a pix "science" x
    #2b mediane/moyenne tempo pix a pix "fond" x
    #3a-opt soustraction mediane ligne / sur ROI "science"  x
    #opt : le faire suivant un masque pixel
    #3b-opt soustraction mediane ligne / sur ROI "fond" x
    #4 prepoc = science - fond x
    #5 creation objet fits avec data = prepoc et header = header premier fichier science 
    
    Returns
    -------
    None.

    '''
    # 1a -
    list_file_science=glob.glob(path_science+'/*'+filebase_science+'*.fits')
    
    hdul_science_0 = fits.open(list_file_science[0])
    xs=np.size(hdul_science_0[exten_no_start].data,axis=0)
    ys=np.size(hdul_science_0[exten_no_start].data,axis=1)
    hdul_science_0.close()
    #print("DEBUG ",xs,ys)
    
    tab_science=np.zeros((xs,ys,len(list_file_science)))
    for n in range(0,len(list_file_science)):
        #print('pre-proc :',n,list_file_science[n])#,end=" "
        print('Loading science data > ',n,list_file_science[n],end='\r',flush=True)
        hdul_science = fits.open(list_file_science[n])
        tempdata=hdul_science[exten_no_start].data
        #
        if n == 0:
            hdul_out=hdul_science
        #3a-opt
        if SubRow_science:
            for i in range(0,xs):
                medval=np.median(tempdata[i,:])
                tempdata[i,:]=tempdata[i,:]-medval
        tab_science[:,:,n]=tempdata
        tempdata=0
        hdul_science.close()
    print('Loading science data > Done',n)
    
    #2a -
    print('Temporal median science data > ...')
    data_raw=np.zeros((xs,ys))
    data_raw=np.median(tab_science,axis=2)

    tab_science=0 # /!\
    print('Temporal median science data > Done')

    # 1b -
    if path_dark != None:
        #print('Dark != None')
        list_file_dark=glob.glob(path_dark+'/*'+filebase_dark+'*.fits')
        
        hdul_dark_0 = fits.open(list_file_dark[0])
        xs=np.size(hdul_dark_0[exten_no_start].data,axis=0)
        ys=np.size(hdul_dark_0[exten_no_start].data,axis=1)
        hdul_dark_0.close()
        
        tab_dark=np.zeros((xs,ys,len(list_file_dark)))
        for n in range(0,len(list_file_dark)):
            #print('pre-proc :',n,list_file_dark[n])
            print('Loading dark data > ',n,list_file_science[n],end='\r',flush=True)
            hdul_dark = fits.open(list_file_dark[n])
            tempdark=hdul_dark[exten_no_start].data
            tab_dark[:,:,n]=tempdark
            tempdark=0
            hdul_dark.close()
        
        print('Loading dark data > Done',n)
        
        #2b -
        print('Temporal median dark data > ...')
        data_dark=np.zeros((xs,ys))
        data_dark=np.median(tab_dark,axis=2)
        print('Temporal median dark data > Done')
        tab_dark=0
        #3b-opt /?\ SUR CHAQUE SINGLE FRAME OU SUR MEDIANE TEMPO ?
        if SubRow_dark:
            print('Soustraction mediane ligne - Dark')
            temp=data_dark
            #print('DEBUG ',temp)
            for i in range(0,xs):
                medval=np.median(data_dark[i,:])
                #print('DEBUG',i,medval)
                data_dark[i,:]=temp[i,:]-medval
            temp=0
    else:
        print('Dark = None')
        data_dark=np.zeros((xs,ys)) 
    
    # 4 -
    data_out=data_raw-data_dark    
    print('Preproc - end')
        
    # save
    hdul_out[0].data=data_out    
  
    # /!\ TODO 2023 01 13 > mediane ligne image science suivant masque pixel masqué
    # /!\ GESTION D'IMAGE AVEC PIXEL MASQUé
    # /v\ ENREGISTREMENT / CREATION D'UN NOUVEAU OBJET HDUL AVEC MEME HEADER QUE 1er FITS ET DATA = IMAGE PRETRATEE
    # /v\ POSSIBILITE D'INSTANCIER IMAGE IMSPOC DIRECTEMENT PAR OBJET HDUL
    
    return data_out,data_raw,data_dark,hdul_out

def image_centroid(image_in):
    '''
    Compute centroid coordinates (first order moment) of a 2D array (image)
    From IDL procedure "cdg.pro"

    Parameters
    ----------
    image_in : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    centroid=np.zeros(2)
    _denom=np.sum(image_in)
    #print(_denom)
    
    for i in range(0,2):
        #print('i ',i)
        _proj=image_in
        for j in range(1,-1,-1):
            #print('j ',j)
            if j != i:
                _proj=np.sum(_proj,axis=j)
        # /?\ /?\ INVERSION X Y ?
        centroid[1-i]=np.sum(_proj*np.arange(np.size(image_in,axis=i)))  

    centroid/=_denom
  
    return centroid  

def make_centerbox_corr(dim, box_s, box_d):#
    '''
    Generation des coordonnées du centre des boites de correlation multi_objet
    Adaotation depuis IDL de flv_make_centerbox_corr.pro

    Returns
    -------
    -------
    None.

    '''
    nbx=int(np.fix(dim[0]/box_d)+1) # number of correlation box along x axis
    nby=int(np.fix(dim[1]/box_d)+1) # number of correlation box along y axis
    tab_center_box=np.zeros((nbx*nby,2)) # array of box center coordinates
    _count=0
    _ix=int(np.fix(nbx/2))
    _iy=int(np.fix(nby/2))
    for a in range(-_ix,_ix):
        for b in range(-_iy,_iy):
            _itemp=[a*box_d+dim[0]/2,b*box_d+dim[1]/2]
            if _itemp[0]+box_s/2 < dim[0] and _itemp[0]-box_s/2 >= 0 and _itemp[1]+box_s/2 < dim[1] and _itemp[1]-box_s/2 >= 0:
                tab_center_box[_count,:]=_itemp
                _count+=1
    
    _indi_0=np.where(tab_center_box[:,0] != 0)
    _indi_1=np.where(tab_center_box[:,1] != 0)
    _indi=_indi_0 and _indi_1
    
    _temp=tab_center_box[_indi[0],:]
    tab_center_box=_temp
    
    return tab_center_box

def corr_multibox(image_in, image_ref, coord_centerbox=None, win_size=None, threshold_perc=0.4):
    '''
    Cross-Correlation between a single or time sequence or collection of images with a reference image 
 
    Returns xy  pixel displacements in each box for each image of image_in
    -------
    None.

    '''
    _dim=np.shape(image_in)
    _ndim=len(_dim)

    if _ndim == 3:
        _xs,_ys,_nim=_dim
    if _ndim == 2:
        _xs,_ys=_dim
        _nim=1
        temp=image_in
        image_in=np.zeros((_xs,_ys,1))
        image_in[:,:,0]=temp
    
    if coord_centerbox is None:
        coord_centerbox=np.zeros((1,2))
        coord_centerbox[0,:]=[int(_xs/2),int(_ys/2)]
        _nbox=1
    
    if len(np.shape(coord_centerbox)) == 1:
        _nbox=1
        temp=coord_centerbox
        coord_centerbox=np.zeros((1,2))
        coord_centerbox[0,:]=temp
    if len(np.shape(coord_centerbox)) == 2:
        _nbox=(np.shape(coord_centerbox))[0]
        
    if win_size is None:
        win_size=np.min((_xs,_ys))
        
    # REFERENCE
    ref_crop_sob=np.zeros((win_size,win_size,_nbox))
    for b in range(0,_nbox): # for each box
        # . Crop    
        ref_crop=image_ref[int(coord_centerbox[b,0]-win_size/2):int(coord_centerbox[b,0]+win_size/2),int(coord_centerbox[b,1]-win_size/2):int(coord_centerbox[b,1]+win_size/2)] 
        # . Sobel filter
        temp=sobel(ref_crop)
        temp/=np.max(temp)
        ref_crop_sob[:,:,b]=temp
    
    # PIXEL DISPLACEMENT
    pix_displ=np.zeros((_nim,_nbox,2))
    for t in range(0,_nim): # for each image
        print('Pixel displacement > ',t,' / ',_nim-1,end='\r',flush=True)
        for b in range(0,_nbox): # for each box
            #print(b)    
            # . Crop
            thu_crop=image_in[int(coord_centerbox[b,0]-win_size/2):int(coord_centerbox[b,0]+win_size/2),int(coord_centerbox[b,1]-win_size/2):int(coord_centerbox[b,1]+win_size/2),t]
            # . Sobel filter
            thu_crop_sob=sobel(thu_crop)
            thu_crop_sob/=np.max(thu_crop_sob)
            # . Correlation
            corr=correlate2d(thu_crop_sob,ref_crop_sob[:,:,b], mode='full', boundary='fill', fillvalue=0)
            #corr=correlate2d(thu_crop_sob,ref_crop_sob[:,:,b], mode='same', boundary='fill', fillvalue=0)
            # . Threshold
            ret, corr_thresh = cv2.threshold(corr, threshold_perc*np.max(corr), 1, cv2.THRESH_TOZERO)
            # . Centroid
            centroid=image_centroid(corr_thresh)
            pix_displ[t,b,:]=centroid-[win_size,win_size]+[1,1]
    
    return pix_displ

# win_s=20     # taille des box de calcul des correlation
# box_dist=4   # distance entre box de calcul
# dim=[96,96]  # zone de calcul

# debug=make_centerbox_corr(dim,win_s,box_dist)    

# fig, (ax) = matplot.pyplot.subplots(1,1,figsize=(12, 12))#,figsize=(8, 6)
# #ax.imshow(lvfspecCal.images[imselect].data*lvfspecCal.images[imselect].mskval,vmin=0,vmax=1000)
# ax.plot(debug[:,0],debug[:,1],'r+') 
# #ax.axis([0,95,0,95])

# ___________________________________________________________
# MAIN CONSTRUCTEUR ET SCRIPT DE TRAITEMENT _________________
# /!\ METTRE EN MAIN POUR EXECUTION SUR JUPYTER
# TODO 2022-11-08
# (> datacube explorer with slidebar)
# x masque de validité pixel
# x definir une classe pour toute acquisition LVF, méthodes associées, et articulation avec lvfdatacalib

# TODO 2022-11-10
# x normalisation datacube zolix par mesure pm101
# > gestion dérive du fond
# > modélisation gaussienne de l'isrf
#   > gestion des exceptions
# > carte isrf pixel
# > function pour masque de validité 
# > definir comment passer isrf suivant type imspoc ?  
# > sort thumbnail par OPD ou lambda croissant
# > passage dans l'espace fov, dev methode de recalage et methode d'estimation de decalage pixel, methode CEA ?
# > test OPENCV
def main():
    # ___________________________________ TRAITEMENT DONNEES DE CALIBRATION SPECTRALE _____________________________________
    # # 1 OLD INSTANCIATION DES FICHIERS DE SCAN SPECTRAUX ZOLIX
    # datapath='C:/Users/goussets/DATA_ACQ/LVF_GEN0/CALIBRATION/20220725_scanZolix/zolix'
    # datafilebasename='scanZolix'
    # lvfspecCal = readfitscube_frommultifile(datapath,datafilebasename)
    
    # 1 INSTANCIATION DES FICHIERS DE SCAN SPECTRAUX ZOLIX
    datapath='C:/Users/goussets/DATA_ACQ/LVF_GEN0/CALIBRATION/20220725_scanZolix/zolix'
    datafilebasename='scanZolix'
    lvfspecCal = readfitscube_frommultifile(datapath,datafilebasename,spectraltag='LAMBDA',_startpix=[1305,548])
    
    imselect=150
    lvfspecCal.images[imselect].set_mskval(winsize=[80,80])
    fig0, (ax0) = matplot.pyplot.subplots(1,1,figsize=(15, 12))#,figsize=(8, 6)
    ax0.imshow(lvfspecCal.images[imselect].mskval)
    ax0.plot(lvfspecCal.images[imselect].centre[:,0],lvfspecCal.images[0].centre[:,1],'r+')    
    
    fig, (ax) = matplot.pyplot.subplots(1,1,figsize=(15, 12))#,figsize=(8, 6)
    ax.imshow(lvfspecCal.images[imselect].data*lvfspecCal.images[imselect].mskval,vmin=0,vmax=1000)
    ax.plot(lvfspecCal.images[imselect].centre[:,0],lvfspecCal.images[0].centre[:,1],'r+')    
    
    fig1, (ax1) = matplot.pyplot.subplots(1,1,figsize=(15, 12))#,figsize=(8, 6)
    ax1.imshow(lvfspecCal.images[0].mskthumbnail)
    ax1.plot(lvfspecCal.images[0].centre[:,0],lvfspecCal.images[0].centre[:,1],'r+')
    
    # # Test library plotly pour slicer graphique cube
    # saff=np.size(lvfspecCal.images)
    # yaff=np.size(lvfspecCal.images[0].data,axis=0)
    # xaff=np.size(lvfspecCal.images[0].data,axis=1)
    # dataaff=np.zeros((yaff,xaff,saff))
    # for i in range(0,saff):
    #     dataaff[:,:,i]=lvfspecCal.images[i].data
    # figanim = px.imshow(dataaff, animation_frame=2, zmin=0,zmax=1000,binary_string=True, labels=dict(animation_frame="slice"))
    # figanim.show()
    
    # 2 LECTURE DES FICHIERS DE MESURE DE PUISSANCE OPTIQUE        
    PM101_path_data='C:/Users/goussets/DATA_ACQ/LVF_GEN0/CALIBRATION/20220725_scanZolix/sv120'
    PM101_filebasename_data='scanPM'
    S120_calibpath='C:/Users/goussets/DATA_ACQ/pm101calib/S120VC_carac.txt'
    
    pm101=readandproc_pm101(PM101_path_data,PM101_filebasename_data,S120_calibpath,plottoscreen=True)
    coef_norm=pm101(lvfspecCal.spectralscale)   # [ph.s-1]
    lvfspecCal.apply_coefnorm(coef_norm)        # normalisation
    
    # fig2, (ax2) = matplot.pyplot.subplots(1,1,figsize=(15, 12))#,figsize=(8, 6)
    # ax2.imshow(lvfspecCal.images[imselect].data*lvfspecCal.images[imselect].mskval)
    # ax2.plot(lvfspecCal.images[imselect].centre[:,0],lvfspecCal.images[0].centre[:,1],'r+')    
    
    # . exemple extraction d'intensité sur les centres des imagettes
    # test2=lvfspecCal.get_3dval([[500,1500]])
    # test2=lvfspecCal.get_3dval(lvfspecCal.images[0].centre)
    test2=lvfspecCal.get_3dval([lvfspecCal.images[0].centre[120],lvfspecCal.images[0].centre[40],lvfspecCal.images[0].centre[300]])
    med=lvfspecCal.get_med(msk=None)
    
    # . exemple de correction du fond
    lvfspecCal.corr_darkdrift(med)
    test3=lvfspecCal.get_3dval([lvfspecCal.images[0].centre[120],lvfspecCal.images[0].centre[40],lvfspecCal.images[0].centre[300]])
    med2=lvfspecCal.get_med(msk=None)

    fig4, (ax4,ax5) = matplot.pyplot.subplots(1,2,figsize=(12, 6))#,figsize=(8, 6)
    fig4.subplots_adjust(wspace=0.1)
    for l in range(0,len(test2)):
        ax4.plot(lvfspecCal.spectralscale,test2[l])  
    ax4.plot(lvfspecCal.spectralscale,med,color='black')
    ax4.set_xlabel('$\lambda$ [nm]')
    ax4.set_ylabel('[ph.s$^{-1}$]')
    ax4.set_title('Before dark drift correction')
    ax4.axis([400,875,-0.5e-10,8*1e-10])
    ax4.grid()
    
    for l in range(0,len(test3)):
        ax5.plot(lvfspecCal.spectralscale,test3[l]) 
    ax5.plot(lvfspecCal.spectralscale,med2,color='black')
    ax5.set_xlabel('$\lambda$ [nm]')
    ax5.set_ylabel('')
    ax5.set_title('After dark drift correction')
    ax5.axis([400,875,-0.5e-10,8*1e-10])    
    ax5.grid()

    # 3 MODELISATION ISRF
    data2fit=lvfspecCal.get_3dval([lvfspecCal.images[0].centre[120]])
    # test=fitlvf_isrf(lvfspecCal)
    
    # # ___________________________________ TRAITEMENT DONNEES SCIENCE _____________________________________
    datapath=r'C:\Users\goussets\DATA_ACQ\LVF_GEN0\20221128_turbiditeSHINE-LVF_V2\acq_LVF'
    datafilebasename='-'
    darkpath=r'C:\Users\goussets\DATA_ACQ\LVF_GEN0\20221128_turbiditeSHINE-LVF_V2\acq_LVF\dark_250cit'
    darkfilebasename='-'
    
    data = preprocess_data(datapath,datafilebasename,exten_no_start=0,path_dark=darkpath,filebase_dark=darkfilebasename,SubRow_dark=True)
    
    temphdul=data[3]
    print(temphdul[0].header)
    ImSPOCinst=ImSPOCDataClass(temphdul[0].data,temphdul[0].header,thumbsize=[96,96],thumbpitch=[96,96],winsize=[80,80],_startpix=[1403,537])
    
    fig, (ax) = matplot.pyplot.subplots(1,1,figsize=(15, 12))#,figsize=(8, 6)
    ax.imshow(ImSPOCinst.data*ImSPOCinst.mskval)#,vmin=0,vmax=1000
    ax.plot(ImSPOCinst.centre[:,0],ImSPOCinst.centre[:,1],'r+')  
    for i in range(0,np.size(ImSPOCinst.centre,axis=0)):
        ax.text(ImSPOCinst.centre[i,0]-48,ImSPOCinst.centre[i,1]+48,str(ImSPOCinst.mskthumbnail[ImSPOCinst.centre[:,:][i,1],ImSPOCinst.centre[:,:][i,0]]),color='white',fontsize=8)
        
    fig1, (ax1) = matplot.pyplot.subplots(1,1,figsize=(15, 12))#,figsize=(8, 6)
    ax1.imshow(ImSPOCinst.mapfov[:,:,0]*ImSPOCinst.mskval)#,vmin=0,vmax=1000
    fig2, (ax2) = matplot.pyplot.subplots(1,1,figsize=(15, 12))#,figsize=(8, 6)
    ax2.imshow(ImSPOCinst.mapfov[:,:,1]*ImSPOCinst.mskval)#,vmin=0,vmax=1000
    
    # ...... Exemple d'interpolation
    t=0
    x=ImSPOCinst.mapfov[ ImSPOCinst.centre[t,1]-int(ImSPOCinst.thumbsize[1]/2):ImSPOCinst.centre[t,1]+int(ImSPOCinst.thumbsize[1]/2), ImSPOCinst.centre[t,0]-int(ImSPOCinst.thumbsize[0]/2):ImSPOCinst.centre[t,0]+int(ImSPOCinst.thumbsize[0]/2) ,0]
    y=ImSPOCinst.mapfov[ ImSPOCinst.centre[t,1]-int(ImSPOCinst.thumbsize[1]/2):ImSPOCinst.centre[t,1]+int(ImSPOCinst.thumbsize[1]/2), ImSPOCinst.centre[t,0]-int(ImSPOCinst.thumbsize[0]/2):ImSPOCinst.centre[t,0]+int(ImSPOCinst.thumbsize[0]/2) ,1]
    z=ImSPOCinst.data[ ImSPOCinst.centre[t,1]-int(ImSPOCinst.thumbsize[1]/2):ImSPOCinst.centre[t,1]+int(ImSPOCinst.thumbsize[1]/2), ImSPOCinst.centre[t,0]-int(ImSPOCinst.thumbsize[0]/2):ImSPOCinst.centre[t,0]+int(ImSPOCinst.thumbsize[0]/2)]
    
    xr=np.reshape(x,(96*96))
    yr=np.reshape(y,(96*96))
    zr=np.reshape(z,(96*96))
    
    interp = CloughTocher2DInterpolator(list(zip(xr, yr)), zr)
    
    fig2, (ax2) = matplot.pyplot.subplots(1,1,figsize=(15, 12))
    ax2.imshow(z)
    
    xrnew=xr+10.2
    yrnew=yr+2
    
    zrnew=interp(list(zip(xrnew,yrnew)))
    zrrnew=np.reshape(zrnew,(96,96))
    
    fig3, (ax3) = matplot.pyplot.subplots(1,1,figsize=(15, 12))
    ax3.imshow(zrrnew)



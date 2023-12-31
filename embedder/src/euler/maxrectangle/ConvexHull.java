package euler.maxrectangle;

import java.awt.Polygon;
import java.awt.Rectangle;
import java.util.*;

public class ConvexHull extends Vector{

    private int start, stop; //tangents for iterative convex hull
    private int xmin,xmax,ymin,ymax;  //position of hull
    int yxmax; //y coord of xmax
    GeomPoint rectp;
    int recth, rectw;
    /* largest rectangles with corners on AC, BD, ABC, ABD, ACD, BCD */
    Vector RectList;  
  
    /* fixed aspect ratio */
    private boolean fixed;
    private int fixedX, fixedY;
    
    public ConvexHull() {
        this.fixed = false;
        this.fixedX = 1;
        this.fixedY = 1;
        RectList = new Vector();
    }
    public ConvexHull(Polygon pol) {
    	this();
    	//System.out.println(pol.npoints);
    	
    	for(int i = 0 ; i < pol.npoints; i++){
    		int x = pol.xpoints[i];
    		int y = pol.ypoints[i];
    		GeomPoint p = new GeomPoint(x,y);
 //   		System.out.println(p.x+ " " + p.y); 
    		this.add(p);
    	}
    	
    /*	System.out.println(this.size());
    	for(int j = 0; j < this.size() ; j++){
    		GeomPoint p = (GeomPoint)this.elementAt(j);
        	System.out.println(p.x+ " " + p.y); 
    	}*/
    	
    	this.computeLargestRectangle();
    }
    
    
    /* position of point w.r.t. hull edge
     * sign of twice the area of triangle abc
     */
    boolean onLeft(GeomPoint a, GeomPoint b, GeomPoint c){
        int area = (b.x -a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y);
        return (area<0);
    }
    
    /* check if point is outside
     * true is point is on right of all vertices
     * finds tangents if point is outside
     */
    boolean pointOutside(GeomPoint p){//, int start, int stop){
        
        boolean ptIn = true, currIn, prevIn = true;
        
        GeomPoint a = (GeomPoint)this.elementAt(0);
        GeomPoint b;
        
        for(int i=0; i<this.size(); i++){
            
            b = (GeomPoint)this.elementAt((i+1)%this.size());
            currIn = onLeft(a, b, p);
            ptIn = ptIn && currIn;
            a = b;
            
            if(prevIn && !currIn){ start = i;} /* next point outside, 1st tangent found */
            if(!prevIn && currIn){ stop = i;}  /* 2nd tangent */
            prevIn = currIn;
            
        }
        return !ptIn;
    }
    
    /* check if point is outside, insert it, maintaining general position */
    /* check if point is outside, insert it, maintaining general position */
    boolean addPointToHull(GeomPoint p) {
        
        /* index of tangents */
        start=0;
        stop=0;
        
        if(!pointOutside(p)){
            return false;
        }
        
        /* insert point */
        int numRemove;
        
        if (stop > start){
            numRemove = stop-start-1;
            if (numRemove>0){
                this.removeRange(start+1, stop);
            }
            this.insertElementAt(p, start+1); //insertElmentAt(p, start+1);
        }
        else{
            numRemove = stop+this.size()-start-1;
            if (numRemove > 0){
                if (start+1 < this.size()){
                    this.removeRange(start+1, this.size());
                }
                if(stop-1 >= 0){
                    this.removeRange(0, stop);
                }
            }
            this.add(p);
          
        }
         return true;
    } 
    /* compute edge list
     * set xmin, xmax
     * used to find largest rectangle by scanning horizontally
     */
    Vector computeEdgeList(){
        Vector l = new Vector();
        GeomPoint a,b;
        GeomEdge e;
        a = (GeomPoint)this.elementAt(this.size()-1);
        for(int i=0; i<this.size(); i++){
        	
        	//System.out.println(i);
            b = (GeomPoint)this.elementAt(i);
            //b = (GeomPoint)this.elementAt(i+1);
            
            if (i==0){
                this.xmin = a.x;
                this.xmax = a.x;
                this.ymin = a.y;
                this.ymax = a.y;
            }
            else{
                if (a.x < this.xmin){
                    this.xmin = a.x;
                }
                if (a.x > this.xmax){
                    this.xmax  = a.x;
                    this.yxmax = a.y;
                }
                if (a.y < this.ymin){
                    this.ymin = a.y;
                }
                if (a.y > this.ymax){
                    this.ymax  = a.y;
                }
            }
            e = new GeomEdge(a,b);
            l.add(e);
            a = b;
        }
        
        
        System.out.println( "xmin:"  + this.xmin + " xmax: " + this.xmax + " ymin:" +
        this.ymin + " ymax:"+ this.ymax + " yxmax:" + this.yxmax);
        return l;
    }
    
    /* compute y intersection with an edge
     * first pixel completely inside
     * ceil function if edge is on top, floor otherwise
     * (+y is down)
     */
    int yIntersect(int xi, GeomEdge e){
        
        int y;
        double yfirst = (e.m) * (xi-0.5) + e.b;
        double ylast = (e.m) * (xi+0.5) + e.b;
        
        if (!e.isTop){
            y = (int)Math.floor(Math.min(yfirst, ylast));
        }
        else {
            y = (int)Math.ceil(Math.max(yfirst, ylast));
        }
        return y;
    }
    
    /* find largest pixel completely inside
     * look through all edges for intersection
     */
    int xIntersect(int y, Vector l){
        int x=0;
        double x0=0, x1=0;
        for(int i=0; i<this.size(); i++){
            GeomEdge e = (GeomEdge)l.elementAt(i);
            if (e.isRight && e.ymin <= y && e.ymax >= y){
                x0 = (double)(y+0.5 - e.b)/e.m;
                x1 = (double)(y-0.5 - e.b)/e.m;
            }
        }
        x = (int)Math.floor(Math.min(x0,x1));
        //System.out.println("xIntersect, x is " + x);
        return x;
    }
    
    GeomEdge findEdge(int x, boolean isTop, Vector l){
        GeomEdge e,emax=(GeomEdge)l.elementAt(0);
        //int count = 0;
        for (int i=0; i<this.size(); i++){
            e = (GeomEdge)l.elementAt(i);
            if (e.xmin == x){
                 if (e.xmax != e.xmin){
                    if ((e.isTop && isTop)||(!e.isTop && !isTop)){
                        emax = e;
                    }
                }
            }
        }
        return emax;
    }
    
    /* compute 3 top and bottom 3 corner rectangle for each xi
     * find largest 2 corner rectangle
     */
    int computeLargestRectangle(){

        Vector edgeList = computeEdgeList();
        this.RectList = new Vector();
        
        GeomEdge top, bottom;
        int ymax, ymin, xright, xlo, xhi;
        int area, maxArea = 0;
        //int maxAreaAC=0, maxAreaBD=0, maxAreaABC=0, maxAreaABD=0, maxAreaACD=0, maxAreaBCD=0;
        int width, height, maxh=0, maxw=0;
      
        /* all 2-corner and 3-corner largest rectangles */
        int aAC=0,aBD=0,aABC=0,aABD=0,aACD=0,aBCD=0;
        GeomPoint pAC, pBD, pABC, pABD, pACD, pBCD;
        int hAC=0,wAC=0,hBD=0,wBD=0,hABC=0,wABC=0,hABD=0,wABD=0,hACD=0,wACD=0,hBCD=0,wBCD=0;
        boolean onA, onB, onC, onD;
        
        GeomPoint maxp = new GeomPoint(0,0);
        pAC = maxp; pBD = maxp; pABC = maxp; pABD = maxp; pACD = maxp; pBCD = maxp;
        
        Vector xint = new Vector();
        
        for(int i=0;i<this.ymax;i++){
            int x = xIntersect(i,edgeList);
            GeomPoint px = new GeomPoint(x,i);
            xint.add(px);
        }
        //find first top and bottom edges
        top = findEdge(this.xmin, true, edgeList);
        bottom = findEdge(this.xmin, false, edgeList);
        
        System.out.println("xint size:" + xint.size());
        
        //scan for rectangle left position
        for(int xi=this.xmin; xi<this.xmax;xi++){
            
            ymin = yIntersect(xi, top);
            ymax = yIntersect(xi, bottom);
            
            for(int ylo = ymax;ylo>ymin;ylo--){//ylo from to to bottom
                
                for(int yhi = ymin; yhi< ymax; yhi++){
                
                    if (yhi>ylo){
                        
                        onA = (yhi == ymax && !bottom.isRight);
                        onD = (ylo == ymin && !top.isRight);
                        
                        xlo = (int)((GeomPoint)xint.elementAt(ylo)).x;//xIntersect(ylo,edgeList);
                        xhi = (int)((GeomPoint)xint.elementAt(yhi)).x;//xIntersect(yhi,edgeList);
                        
                        xright = maxp.min(xlo,xhi);
                        onC = (xright == xlo && this.yxmax >= ylo);
                        onB = (xright == xhi && this.yxmax <= yhi);
                        
                        height = yhi-ylo;
                        width = xright - xi;
                            
                        if (!this.fixed){                                                      
                        }//!fixed
                        else{
                          int fixedWidth = (int)Math.ceil( ((double) height*this.fixedX)/((double)this.fixedY));
                          if (fixedWidth <= width){
                              width = fixedWidth;
                          }
                          else{
                              width = 0;
                          }
                       }
                        area = width * height;
                        //AC 
                        if (onA && onC && !onB && !onD){                            
                            if (area > aAC){
                                aAC = area;
                                pAC = new GeomPoint(xi, ylo);
                                hAC = height;
                                wAC = width;
                            }
                        }
                        //BD
                        if (onB && onD && !onA && !onC){
                            if (area > aBD){
                                aBD = area;
                                pBD = new GeomPoint(xi, ylo);
                                hBD = height;
                                wBD = width;
                            }
                        }
                        //ABC
                        if (onA && onB && onC){
                            if (area > aABC){
                                aABC = area;
                                pABC = new GeomPoint(xi, ylo);
                                hABC = height;
                                wABC = width;
                            }
                        }
                        //ABD
                        if (onA && onB && onD){
                            if (area > aABD){
                                aABD = area;
                                pABD = new GeomPoint(xi, ylo);
                                hABD = height;
                                wABD = width;
                            }
                        }
                        //ACD
                        if (onA && onC && onD){
                            if (area > aACD){
                                aACD = area;
                                pACD = new GeomPoint(xi, ylo);
                                hACD = height;
                                wACD = width;
                            }
                        }
                        //BCD
                        if (onB && onC && onD){
                            if (area > aBCD){
                                aBCD = area;
                                pBCD = new GeomPoint(xi, ylo);
                                hBCD = height;
                                wBCD = width;
                            }
                        }
                        
                        if(area>maxArea){
                            maxArea = area;
                            maxp = new GeomPoint(xi, ylo);
                            maxw = width;
                            maxh = height;
                           // System.out.println(onA + " " + onB + " " + onC + " " + onD);
                        }
                    }//yhi > ylo
                }//for yhi
            }//for ylo
            if (xi == top.xmax){
                top = findEdge(xi,  true, edgeList);
            }
            if(xi == bottom.xmax){
                bottom = findEdge(xi, false, edgeList);
            }
        }//xi
        this.rectp = maxp;
        this.recth = maxh;
        this.rectw = maxw;
        
        this.RectList.add(new Rectangle(pAC.x, pAC.y, wAC, hAC));
        this.RectList.add(new Rectangle(pBD.x, pBD.y, wBD, hBD));
        this.RectList.add(new Rectangle(pABC.x, pABC.y, wABC, hABC));
        this.RectList.add(new Rectangle(pABD.x, pABD.y, wABD, hABD));
        this.RectList.add(new Rectangle(pACD.x, pACD.y, wACD, hACD));
        this.RectList.add(new Rectangle(pBCD.x, pBCD.y, wBCD, hBCD));
        this.RectList.add(new Rectangle(maxp.x, maxp.y, maxw, maxh));
        return 0;
        
    }
    
    public Rectangle getMaxRectangle(){
    	return  (Rectangle)RectList.elementAt(6);
    	
    }
    
}
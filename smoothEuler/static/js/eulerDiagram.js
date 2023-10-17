class EulerDiagram{
    constructor(eulerDiagramData, divId) { 
        this.jsonData = eulerDiagramData;
        this.divId = divId;
        this.initLayout();
        // svg elements
        this.svg = d3.select(`#${divId}`).select('svg');
        d3.select(`#${divId}`).attr('selected', false); // set unselected
        this.eulerGroup = this.svg.append('g')
            .attr('transform', `translate(${-this.jsonData['range']['x']}, ${-this.jsonData['range']['y']})`); 
        this.tooltip = '';
        // each part of svg
        this.zonesG = this.eulerGroup.append('g');
        this.curvesG = this.eulerGroup.append('g').classed('curvesG', true);
        this.triangulationEdgesG = this.eulerGroup.append('g'); 
        this.curvesNameG = this.eulerGroup.append('g'); 
        this.zonesNameG = this.eulerGroup.append('g');
        this.mergeInfo = '';  // write down the merge information at the middle bottom of svg
        this.edgesG = this.eulerGroup.append('g');
        // data 
        this.curves = eulerDiagramData['curves'];
        this.triangulationEdges = eulerDiagramData['triangulationEdges'];
        this.zones = eulerDiagramData['abstractDiagram'];
        this.mirrorCurves = this.curves;
        this.edges = eulerDiagramData['zoneGraph'];
        this.zonesDict = this.getZonesDict();
    }

    // setup the width and height of div and svg and merge info
    initLayout(){
        d3.select(`#${this.divId}`).select('svg').selectAll('*').remove();
        d3.select(`#${this.divId}`)
            .style('width', `${globalSetup['range']['width']+globalSetup['svgPadding']['left']+globalSetup['svgPadding']['right']}px`)
            .style('height', `${globalSetup['range']['height']+globalSetup['svgPadding']['top']+globalSetup['svgPadding']['bottom']}px`);
        d3.select(`#${this.divId}`).select('svg')
            .style('width', `${this.jsonData['range']['width']}px`)
            .style('height', `${this.jsonData['range']['height']}px`);
        // also set the width of #mergeInfoContainer
        d3.select('#mergeInfoContainer').style('width', parseInt(d3.select(`#${this.divId}`).style('width'))*2+'px');
    }   

    // transform a list of coordinates into a path string
    pathGenarator(coordinates){
        let pathString = '';
        for(let idx in coordinates){
            let substr = idx == 0? `M${coordinates[idx]['x']} ${coordinates[idx]['y']} `:`L${coordinates[idx]['x']} ${coordinates[idx]['y']} `; 
            pathString += substr;
        }
        pathString += ' Z';
        return pathString;
    }

    // get the zone ~ coordinate dict {'zoneLabel': {x: , y: }}
    getZonesDict(){
        let zonesDict = {};
        console.log("this.zones",  this.zones);
        this.zones.forEach(item => {
        zonesDict[item['zone']] = item['coordinate'];
        });
        return zonesDict;
    }

    // visualize the trigangules
    visTriangules(){
        this.triangulationEdgesG.style('opacity', setup.triangulation?1:0);
        this.curvesNameG.style('opacity', setup.triangulation?1:0);
        this.triangulationEdgesG.selectAll('line').data(this.triangulationEdges)  // edges of triangulars
            .join('line')
            .attr('x1', d=>d['edge']['startX'])
            .attr('x2', d=>d['edge']['endX'])
            .attr('y1', d=>d['edge']['startY'])
            .attr('y2', d=>d['edge']['endY'])
            .attr('stroke', 'grey')
            .attr('stroke-width', '0.5');
        this.curvesNameG.selectAll('text').data(this.triangulationEdges) // edge label
            .join('g')
            .filter(d=>d['edge']["cut points"].length)
            .each(function(d){
                let group = d3.select(this).append('g');
                group.selectAll('text').data(d['edge']["cut points"])
                    .join('text')
                    .text(_d=>_d["cutPoint"]["sets"])
                    .attr('x', _d=>_d["cutPoint"]["x"])
                    .attr('y', _d=>_d["cutPoint"]["y"])
                    .attr('text-anchor', 'middle')
                    .attr('dominant-baseline', 'central')
                    .attr('fill', 'grey');
            });
    }

    // visualize the curves and curve names
    visCurves(curves = '', rerender=false){
        let that = this;
        if(!curves){
            curves = this.mirrorCurves;
        }
        let curveLst = [];
        for(let i in curves){
            curveLst.push(curves[i]['curve']['name']);
        }

        // judge if the curve name  is a lower case
        const isLowerCase = (str)=>{
            return str === str.toLowerCase() &&
                   str !== str.toUpperCase();
        } 

        this.curvesG.selectAll('path').data(curves)  // curve
        .join('path')
        .each(function(d){
            let curveName = d['curve']['name'];
            let isHole = !isLowerCase(curveName);
            let isHoleSet = isLowerCase(curveName)&&(curveLst.includes(curveName.toUpperCase()));
            d3.select(this).attr('class', `${curveName}Curve`)
                .attr('d', that.pathGenarator(d['curve']['coordinates']))
                .attr('stroke', colorScheme[EulerSets.indexOf(curveName.toLowerCase())])
                .style('stroke-width', isHole||isHoleSet? "2px": "2px")
                .attr('fill', isHole? "grey": colorScheme[EulerSets.indexOf(curveName.toLowerCase())])
                .style('fill-opacity', 0.3); 
        });
        // set select all
        d3.select('#Eulerlegend').select('table')
            .selectAll('input').property('checked', true);
    }

    updateVisCurves(curves = ''){
        if(!curves){
            curves = this.mirrorCurves;
        }
        this.visCurves(curves, true);
    }

    // visualize zones and zone labels
    visZones(){
        this.zonesG.selectAll('circle').data(this.zones)  // zones
            .join('circle')
            .attr('cx', d=>d['coordinate']['x'])
            .attr('cy', d=>d['coordinate']['y'])
            .attr('r', 13)
            .attr('fill', 'white')
            .attr('stroke', 'grey')
            .attr('stroke-width', '1');
        this.zonesNameG.selectAll('text').data(this.zones) // zone label
            .join('text')
            .text(d=>d['zone']=='f'||d['zone']=='dfm'?d['zone']:d['zone'])
            // .text(d=>d['zone']=='f'||d['zone']=='dfm'?d['zone']:d['zone'])
            .attr('x', d=>d['coordinate']['x'])
            .attr('y', d=>d['coordinate']['y'])
            .attr('dominant-baseline', 'central')
            .attr('text-anchor', 'middle')
            .style('font-size', '10px')
            .attr('color', 'grey')
            .attr('dy', '0em');
        this.zonesNameG.selectAll('text').raise();
    }

    // visualize the label
    visLabel(){
        let that = this;
        this.curvesG.selectAll('path')
            .each(function(){
                let setName = d3.select(this).datum()['curve']['name'];
                let coordinates = d3.select(this).datum()['curve']['coordinates'];
                let coodinateX = d3.mean(coordinates, d=>d.x);
                let coodinateY = d3.mean(coordinates, d=>d.y);
                that.curvesG.append('text')
                    .text(info['mapping'][setName])
                    .attr('x', coodinateX)
                    .attr('y', coodinateY)
                    .style('fill', colorScheme[info['sets'].indexOf(setName)]);
            });

    }

    // visualize the dual graph
    visGraph(){
        this.visZones();
        // this.edgesG.style('opacity', concurrencySetup.zoneGraph?1:0);
        this.edgesG.selectAll('line').data(this.edges)  // edges of triangulars
            .join('line')
            .attr('x1', d=>this.zonesDict[d['from']]['x'])
            .attr('x2', d=>this.zonesDict[d['to']]['x'])
            .attr('y1', d=>this.zonesDict[d['from']]['y'])
            .attr('y2', d=>this.zonesDict[d['to']]['y'])
            .attr('stroke', 'grey')
            .attr('stroke-width', '0.5');
    }

    // hilight the merge sets at the current euler diagram.
    visMergeInfo(){
        if(!concurrencySetup.setMerging){return;}
        let mergeLst = info['deconcurrency']['merges'][focusMergeId-1];
        if(this.divId=='leftEuler'){
            this.curvesG.select(`.${mergeLst[0]}Curve`).attr('stroke-width', '2px');
            this.curvesG.select(`.${mergeLst[1]}Curve`).attr('stroke-width', '2px');
        }
        else{
            this.curvesG.select(`.${mergeLst[0]}Curve`).attr('stroke-width', '2px');
        }
    }
    /**mouse over one curve */
    mouseoverCurve(event, element){
        // d3.select(element).style('stroke-width', '2px');   // highlight the curve border
        let set = d3.select(element).attr('class').slice(0, 1);
        let fillOpacity = d3.select(element).style('fill-opacity');
        d3.select(element).style('fill-opacity', d3.max([fillOpacity, 0.2])); // change fill opacity
        this.createTooltip(event.offsetX, event.offsetY, set);
    }
    mouseoutCurve(event, element){
        // d3.select(element).style('stroke-width', null);   // dehighlight the curve border
        let fillOpacity = d3.select(element).style('fill-opacity');
        d3.select(element).style('fill-opacity', fillOpacity>0.3?fillOpacity:0);
        this.tooltip.remove();
    }
    mousemoveCurve(event, element){
        let moveX = event.movementX;
        let moveY = event.movementY;
        let rect = this.tooltip.select('rect');
        let text = this.tooltip.select('text');
        rect.attr('x', parseInt(rect.attr('x'))+moveX)
            .attr('y', parseInt(rect.attr('y'))+moveY);
        text.attr('x', parseInt(text.attr('x'))+moveX)
            .attr('y', parseInt(text.attr('y'))+moveY);
    }
    clickCurve(){
        let set = d3.select(this).attr('class').slice(0, 1);
        let fillOpacity = d3.select(this).style('fill-opacity');
        let isselected = fillOpacity>0.1;   // if the current curve has been selected
        d3.select(this).style('fill-opacity', isselected?0:0.11);
        // select or deselect the set in the set information table
        let checkBoxHTML = d3.select('#setInfoDiv').select(`.row-${set}`)
            .select('input').property('checked', !isselected).node();
        setSelection(checkBoxHTML);
    }
    createTooltip(x, y, set){
        this.tooltip = this.svg.append('g')
        this.tooltip.append('rect')
            .attr('x', x+10)
            .attr('y', y+10)
            .attr('rx', 5)
            .attr('width', 35)
            .attr('height', 35)
            .style('fill', 'white')
            .style('fill-opacity', 0.9);
        this.tooltip.append('text')
            .attr('x', x+27.5)
            .attr('y', y+27.5)
            .attr('dy', '0.3em')
            .attr('text-anchor', 'middle')
            .style('fill', colorScheme[parseInt(info['sets'].indexOf(set))])
            .style('font-size', '20px')
            .style('font-weight', 'bold')
            .text(set);
    }



    // visualize all elements
    visAll(){
        this.visTriangules();
        this.visGraph();
        this.visCurves();
        this.edgesG.lower();
    }
}
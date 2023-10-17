const colorScheme = ['#4e79a7', '#76b7b2', '#f28e2c', '#e15759', '#59a14f', '#edc949', '#af7aa1', '#ff9da7', '#aec7e8', '#9467bd', '#ffbb78', 
    '#dbdb8d', '#98df8a', '#1f77b4', '#c5b0d5', '#7f7f7f', '#bcbd22'];  // '#9c755f', '#bab0ab', '#d62728', 
let colorMap = {}; 
let EulerData = '';
let EulerObj = '';
let setup = {   // control panel setup
  triangulation: false,
  zoneGraph: true,
}
let EulerSets = []; // all sets in this euler data

const globalSetup = {
  dataName: 'eulerData',
  range: {width: 300, height: 300},  // the range for the euler diagram
  svgPadding: {left: 10, right: 10, top: 10, bottom: 10},
  smooth: {iteration: 50, distance: 5},
}

// get the range of the two euler diagrams, and get the range of the div (can contain both diagrams)
function initDiagramRange(leftDigramData, rightDigramData){
  // for each data add a key called 'range'{'x', 'y', 'width', 'height'}
  let getWidHei = (eulerDiagramData)=>{
    let allXValues = [];
    let allYValues = [];
    let edgeLst = eulerDiagramData['triangulationEdges'];
    for(idx in edgeLst){
      let edge = edgeLst[idx]['edge'];
      allXValues.push(edge['startX']);
      allXValues.push(edge['endX']);
      allYValues.push(edge['startY']);
      allYValues.push(edge['endY']);
    }
    let [minX, maxX, minY, maxY] = [...d3.extent(allXValues), ...d3.extent(allYValues)];
    eulerDiagramData['range'] = {};
    eulerDiagramData['range']['x'] = minX;
    eulerDiagramData['range']['y'] = minY;
    eulerDiagramData['range']['width'] = maxX - minX;
    eulerDiagramData['range']['height'] = maxY - minY;
    return [maxX - minX, maxY - minY];
  };
  let [leftWid, leftHei] = getWidHei(leftDigramData);
  let [rightWid, rightHei] = getWidHei(rightDigramData);
  globalSetup['range']['width'] = d3.max([leftWid, rightWid]);
  globalSetup['range']['height'] = d3.max([leftHei, rightHei]);
  globalSetup['svgPadding'] = {left: 10, right: 10, top: 10, bottom: 10};
}

// get all sets in this euler diagram
function initEulerSets(eulerdata){
  let allcurves = eulerdata['curves'];
  for (const curve of allcurves) {
    EulerSets.push(curve['curve']['name']);
  }
  console.log('EulerSets', EulerSets);
}

// visualize legend and initialize the click event
function visualizeLegend(){
  if(focusStepId!=3){return;}
}


// add smooth listener
function addListner(){
  d3.select('#smoothBtn').on('click', smoothEuler);
  d3.select('#restoreBtn').on('click', restoreEuler);
  d3.select('#iterationInput').on('change', updateIteration);
  d3.select('#distanceInput').on('change', updateDistance);
  d3.select('#selectBox').on('change', updateSelect);
  d3.select('#triangleBox').on('change', updateTriangle);
  d3.select('#graphBox').on('change', updateZoneGraph);
}

// when load the page for the first time, then we will tell the backend which data being used
function loaded(){
  axios.post('/init', {
    dataName: globalSetup.dataName
    })
    .then((result) => {
        // let curves = result['data'];
    }).catch((err) => {
        console.log(err);
    });
}

function smoothEuler(){
  axios.post('/smooth', {
      iteration: globalSetup.smooth.iteration,
      distance: globalSetup.smooth.distance,
      step: '',
    })
    .then((result) => {
        let curves = result['data'];
        console.log(curves);
        EulerObj.updateVisCurves(curves);
    }).catch((err) => {
        console.log(err);
    });
}

// visualize the unsmoothed version
function restoreEuler(){
  EulerObj.updateVisCurves(EulerObj.curves);
}

// update the value of Iteration
function updateIteration(){
  console.log('update the iteration');
  globalSetup.smooth.iteration = parseInt(d3.select('#iterationInput').node().value);
}

// update the value of Distance
function updateDistance(){
  globalSetup.smooth.distance = parseInt(d3.select('#distanceInput').node().value);
}

// Select all sets or deselect all sets
function updateSelect(){
  // if select all, then all texts highlight, and all path fill
  if(d3.select('#selectBox').node().checked){
    d3.selectAll('.setClass')
      .property('status', 1)
      .style('color', (d, i)=>colorScheme[i])
      .style('font-weight', 700);
    focusLeft.curvesG.selectAll('path')
      .style('fill-opacity', 0.5);
    focusRight.curvesG.selectAll('path')
      .style('fill-opacity', 0.5);
  }
  else{
    // if deselect all, then all texts dehighlight, and all path none
    d3.selectAll('.setClass')
      .property('status', 0)
      .style('color', null)
      .style('font-weight', null);
    focusLeft.curvesG.selectAll('path')
      .style('fill-opacity', 0);
    focusRight.curvesG.selectAll('path')
      .style('fill-opacity', 0);
  }
}

/**
 * reveal or hidden the triangle lines
 */
function updateTriangle(){
  setup.triangulation = d3.select('#triangleBox').node().checked;
  let opacity = setup.triangulation? 1:0;
  EulerObj.triangulationEdgesG.style('opacity', opacity);
  EulerObj.curvesNameG.style('opacity', opacity);
}

function updateZoneGraph(){
  setup.zoneGraph = d3.select('#graphBox').node().checked;
  let zoneGraphG =  d3.selectAll([...EulerObj.edgesG, ...EulerObj.zonesG, ...EulerObj.zonesNameG]);
  zoneGraphG.style('visibility', setup.zoneGraph? "visible" : "hidden");
}

/**
 * Load the unsmoothed Euler data
 */
async function loadData(){
  EulerData = await d3.json(`../static/data/eulerData/EulerJSON-2.json`);
  initDiagramRange(EulerData, EulerData);
  initEulerSets(EulerData);
}

loadData().then(()=>{
  EulerObj = new EulerDiagram(EulerData, "Eulergraph");
  EulerObj.visAll();
  addListner();
  loaded();
  // visualize the legend
  visLegend();
});
/**
 * This script is used to render and control the set information div
 */
function visLegend(){
  let table = d3.select('#Eulerlegend').select('table').select('tbody');
  table.selectAll('*').remove();

  // render all data
  table.selectAll('trow').data(EulerSets)
    .join('tr')
    .each(function(d){
      d3.select(this).classed(`row-${d}`, true)  // class for each row, used for searching this row when hilighting it 
      let isfilled = false;
      try{
        isfilled = EulerObj.svg.select(`.${d}Curve`).style('fill-opacity')!=0;  //   if this curve is already filled, then set checked true
      }
      catch{
        isfilled = false;
      }
      // add the checkbox
      d3.select(this).append('td').classed('checkBoxtd', true)
        .append('input')
        .attr('type', 'checkbox')
        .classed(`checkbox-${d}`, true)
        .property('set', d)
        .style('visibility', 'visible')
        .style('accent-color', colorScheme[parseInt(EulerSets.indexOf(d))])
        .on('change',  function(){
          setSelection(this);
        })
        .property('checked', isfilled);
      // add the set td
      d3.select(this).append('td').text(d)
        .style('color', colorScheme[parseInt(EulerSets.indexOf(d))]);
    });
  // add listener on the 'All' button
  d3.select('#Eulerlegend').select('table')
    .select('.selectAllRow')
    .style('visibility', 'visible')
    .select('.checkbox-All')
    .property('checked', true)
    .on('change', function(){
      setSelection(this);
    });
}

/**
 * when select/unselect a set
 * 1. update the style of row that checkbox in
 * @param {HTML element} element - the HTML element of the checkbox
 */
function setSelection(element){
  let table = d3.select('#Eulerlegend').select('table').select('tbody');
  let isAllCheckBox = d3.select(element).attr('class')=='checkbox-All'; 
  let isChecked = d3.select(element).node().checked;

  if(!isAllCheckBox){ // select a set
    let set = d3.select(element).property('set');
    // check if all set are checked, then the select all will be checked as well 
    let allChecked = true;
    for(let setid in EulerSets){
      if(!table.select(`.checkbox-${EulerSets[setid]}`).node().checked){
        allChecked = false;
      }
    } 
    d3.select('#Eulerlegend').select('.checkbox-All').property('checked', allChecked);
    table.select(`.row-${set}`).classed('highlight', isChecked);
    console.log("enter into here", set);
    EulerObj.svg.selectAll(`.${set}Curve`).style('fill-opacity', isChecked?0.4:0);
    EulerObj.svg.selectAll(`.${set}Curve`).raise();
    let opa = parseFloat(EulerObj.svg.selectAll(`path`).style('stroke-opacity'));
  }
  else{
    table.selectAll('input').property('checked', isChecked)
    table.selectAll('tr').classed('highlight', isChecked);
    EulerObj.svg.select('.curvesG').selectAll('path').style('fill-opacity', isChecked?0.4:0);
  }
}
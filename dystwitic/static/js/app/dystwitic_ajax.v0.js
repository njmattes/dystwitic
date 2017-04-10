
var wrap = d3.select('.wrapper.map')
  , pixels
  , map_data
;

var draw_map = function draw_map() {
  pixels = wrap.selectAll('.pixel')
    .data(map_data)
    .enter()
    .append('div')
    .classed('pixel', true)
    .style('background-color', function(d) {
      return d3.color(d3.rgb(d[0]*255, d[1]*255, d[2]*255)); })
};

var update_fills = function update_fills() {
  pixels.data(map_data)
    .style('background-color', function(d) {
      return d3.color(d3.rgb(d[0]*255, d[1]*255, d[2]*255)); })
};

var update_map = function update_map() {
  d3.json('/get_map', function(err, data) {
    map_data = data['map'];
    console.log(map_data.length, map_data[0]);
    update_fills();
  });
};

d3.json('/get_map', function(err, data) {
  map_data = data['map'];
  draw_map();
});

setInterval(update_map, 1000);
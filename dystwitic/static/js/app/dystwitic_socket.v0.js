
var wrap = d3.select('.wrapper.map')
  , pixels = wrap.selectAll('.pixel')
  , map_data
;

var socket = io();
var t = new Date().getSeconds() + 60;

var update_fills = function update_fills() {
  pixels.data(map_data)
    .style('background-color', function(d) {
      return d3.color(d3.rgb(d[0]*255, d[1]*255, d[2]*255)); })
};

socket.on('connect', function() {
  socket.emit('my request', {'t': t, 'f': 1});
});

socket.on('my response', function(data) {
  if (data['map'].length > 0) {
    map_data = JSON.parse(data['map']);
    t = data['t'];
    update_fills();
  }
  socket.emit('my request', {'t': t, 'f': 0});
});

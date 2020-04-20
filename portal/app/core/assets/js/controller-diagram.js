var diagram = new SimpleDiagram('#diagram', {
    cellSize: window.innerWidth*0.04,
    numColumns: 11,
    numRows: 9,
    interactive: false
});

var nodes = [
    {name: 'A', row: 5, column: 1, connectsTo: 'D', shape: 'grid', source: './'},
    {name: 'B', row: 1, column: 9, connectsTo: 'D', shape: 'solar_panel', source: './', color: 'reds'},
    {name: 'C', row: 3, column: 10, connectsTo: 'D', shape: 'washer', source: './', color: 'reds'},
    {name: 'D', row: 5, column: 4, shape: 'house', source: './', color: 'reds'},
    {name: 'E', row: 7, column: 10, connectsTo: 'D', shape: 'battery', source: './', color: 'reds'},
    {name: 'F', row: 9, column: 9, connectsTo: 'D', shape: 'charger', source: './', color: 'reds'},
    {name: 'G', row: 5, column: 11, connectsTo: 'D', shape: 'hvac', source: './', color: 'reds'},
];

// Draw the nodes!

nodes.forEach(function(node) {

    diagram.addNode({
        shape: node.shape,
        name: node.name,
        label: node.name,
        row: node.row,
        column: node.column,
        source: node.source,
        color: node.color
    });

});

// Draw the links!

nodes.forEach(function(node) {

    if (!node.connectsTo)
        return;

    diagram.addLine({
        from: node.name,
        to: node.connectsTo
    });

});

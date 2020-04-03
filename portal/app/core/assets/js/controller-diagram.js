var diagram = new SimpleDiagram('#diagram', {
    cellSize: window.innerWidth*0.04,
    numColumns: 9,
    numRows: 9,
    interactive: false
});

var nodes = [
    {name: 'A', row: 5, column: 1, connectsTo: 'D', shape: 'grid', source: './'},
    {name: 'B', row: 2, column: 8, connectsTo: 'D', shape: 'solar_panel', source: './'},
    {name: 'C', row: 4, column: 9, connectsTo: 'D', shape: 'washer', source: './'},
    {name: 'D', row: 5, column: 4, shape: 'house', source: './'},
    {name: 'E', row: 6, column: 9, connectsTo: 'D', shape: 'battery', source: './'},
    {name: 'F', row: 8, column: 8, connectsTo: 'D', shape: 'charger', source: './'},
];

// Draw the nodes!

nodes.forEach(function(node) {

    diagram.addNode({
        shape: node.shape,
        name: node.name,
        label: node.name,
        row: node.row,
        column: node.column,
        source: node.source
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

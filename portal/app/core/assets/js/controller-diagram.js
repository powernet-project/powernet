var diagram = new SimpleDiagram('#diagram', {
    cellSize: 70,
    numColumns: 9,
    numRows: 9,
    interactive: false
});

var nodes = [
    {name: 'A', row: 4, column: 2, connectsTo: 'D', shape: 'solar_panel', source: './'},
    {name: 'B', row: 2, column: 5, connectsTo: 'D', shape: 'grid', source: './'},
    {name: 'C', row: 4, column: 8, connectsTo: 'D', shape: 'washer', source: './'},
    {name: 'D', row: 5, column: 5, shape: 'house', source: './'},
    {name: 'E', row: 8, column: 2, connectsTo: 'D', shape: 'battery', source: './'},
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

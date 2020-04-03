var diagram = new SimpleDiagram('#diagram', {
<<<<<<< HEAD
    cellSize: window.innerWidth*0.04,
=======
    cellSize: 70,
>>>>>>> 0d3caa6f0a08104a9b3fe4ba62b0e811f3836b7c
    numColumns: 9,
    numRows: 9,
    interactive: false
});

var nodes = [
<<<<<<< HEAD
    {name: 'A', row: 5, column: 1, connectsTo: 'D', shape: 'grid', source: './'},
    {name: 'B', row: 2, column: 8, connectsTo: 'D', shape: 'solar_panel', source: './'},
    {name: 'C', row: 4, column: 9, connectsTo: 'D', shape: 'washer', source: './'},
    {name: 'D', row: 5, column: 4, shape: 'house', source: './'},
    {name: 'E', row: 6, column: 9, connectsTo: 'D', shape: 'battery', source: './'},
=======
    {name: 'A', row: 4, column: 2, connectsTo: 'D', shape: 'solar_panel', source: './'},
    {name: 'B', row: 2, column: 5, connectsTo: 'D', shape: 'grid', source: './'},
    {name: 'C', row: 4, column: 8, connectsTo: 'D', shape: 'washer', source: './'},
    {name: 'D', row: 5, column: 5, shape: 'house', source: './'},
    {name: 'E', row: 8, column: 2, connectsTo: 'D', shape: 'battery', source: './'},
>>>>>>> 0d3caa6f0a08104a9b3fe4ba62b0e811f3836b7c
    {name: 'F', row: 8, column: 8, connectsTo: 'D', shape: 'charger', source: './'},
];

// Draw the nodes!

nodes.forEach(function(node) {
<<<<<<< HEAD
=======

>>>>>>> 0d3caa6f0a08104a9b3fe4ba62b0e811f3836b7c
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

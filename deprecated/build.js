#! /usr/bin/env node

var fs = require( 'fs' );
var sqlite = require( 'sqlite3' ).verbose();


var file_sql = './src/index.sql';
var file_db = './Emmet.docset/Contents/Resources/docSet.dsidx';
var table_drop = 'DROP TABLE IF EXISTS searchIndex';
var table_create = 'CREATE TABLE searchIndex (id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)';
var index_create = 'CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)';
var index_add = "INSERT INTO searchIndex (name, type, path) VALUES (?, ?, ?)";


var db = new sqlite.Database( file_db );
db.serialize(function() {
    // prepare
    db.run( table_drop, function ( err ) {
        if ( err ) console.info( 'table drop fail: %s', err );
    });
    db.run( table_create, function( err ) {
        if ( err ) console.info( 'table create fail: %s', err );
    });
    db.run( index_create, function( err ) {
        if ( err ) console.info( 'index create fail: %s', err );
    });

    // fill
    var stmt = db.prepare( index_add );
    fs.readFileSync(
        file_sql, 'utf-8'
    ).split( '\r' ).forEach(function ( line ) {
        line = line.split( '|' );
        stmt.run( line[ 2 ], line[ 0 ], 'index.html#' + line[ 1 ] );
    });
    stmt.finalize();

    // // dump
    // db.each( "SELECT * FROM searchIndex", function( err, row ) {
    //     console.log( row );
    // });
});

db.close();


// others
// ....

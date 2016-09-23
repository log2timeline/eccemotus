var LateralMap = (function() {

    var Map = function() {};
    Map.prototype.setData = function(data) {
        /* Makes revertible data manipulation possible. */
        // Permanent copy of data.
        this.backupData = JSON.parse(JSON.stringify(data));
        // Working data.
        this.graph = JSON.parse(JSON.stringify(data));
    }

    Map.prototype.reset = function() {
        /* Reset working data to initial data. */
        this.graph = JSON.parse(JSON.stringify(this.backupData));
    }

    Map.prototype.setForces = function() {
        /* Set up simulation forces that control positions of elements. */
        var THAT = this;
        this.simulation = d3.forceSimulation(this.graph.nodes).on('tick', function() {
                THAT.tick();
            })
            .force('link', d3.forceLink(this.graph.links)
                .id(function(d) {
                    return d.id;
                })
                .strength(function(d) {
                    return linkStrength(d);
                })
                .distance(function(d) {
                    return linkDistance(d);
                })
            )
            .force('charge', d3.forceManyBody()
                .distanceMax(500)
                .strength(-200))
            .force('machine', filteredManyBody()
                .distanceMax(1000)
                .strength(-20000))
            .force('centering', d3.forceCenter(this.width / 2, this.height / 2))
            .stop();
    }

    Map.prototype.setElements = function() {
        /* Create d3 element and link them to data. */
        var THAT = this;
        this.holder.selectAll('*').remove();
        this.glinks = this.holder.append('g')
            .attr('class', 'links')
            .selectAll()
            .data(graph.links)
            .enter().append('g')
                .attr('class', 'link')
                .attr('id', function(d) {
                    return 'glink_' + d.index;
                });

        this.links = this.glinks.append('line')
            .attr('stroke', linkColor)
            .attr('stroke-opacity', 0.5)
            .style('marker-start', function(d) {
                return d.type == 'access' ? 'url(#mid-arrow)' : '';
            })
            .attr('stroke-width', THAT.vars.linkWidth)
            .on('click', function(d) {
                console.log(d);
                var  i=0;
                var minTime = 2439118792937500;
                var maxTime = 0;
                for(var e in d.events) {
                    minTime = Math.min(minTime, d.events[e].timestamp);
                    maxTime = Math.max(maxTime, d.events[e].timestamp);
                    i+=1;
                    if (i<10){
                        console.log(d.events[e]);
                    }
                }
                console.log(minTime, maxTime);
            })
            .on('mouseover', function(d) {
                glink = d3.select(this.parentNode);
                var line = glink.select('line');
                var newWidth = 2 * THAT.vars.linkWidth / THAT.oldScale;
                line.attr('stroke-width', newWidth);

                var text = glink.select('text');
                var newFontSize = 2 * THAT.vars.fontSize / THAT.oldScale;
                text.style('font-size', newFontSize);
            })
            .on('mouseout', function(d) {
                glink = d3.select(this.parentNode);
                var line = glink.select('line');
                var current = line.attr('stroke-width').replace('px', '');
                line.attr('stroke-width', THAT.vars.linkWidth / THAT.oldScale);

                var text = glink.select('text');
                var newFontSize = THAT.vars.fontSize / THAT.oldScale;
                text.style('font-size', newFontSize);
            });

        this.linkLabels = this.glinks.append('text')
            .text(function(d) {
                return d.events.length;
            })
            .style('opacity', 0.5)
            .style('font-size', THAT.vars.fontSize)
            .attr('class', 'linklabel');

        this.gnodes = this.holder.append('g')
            .attr('class', 'nodes')
            .selectAll()
            .data(graph.nodes)
            .enter()
            .append('g')
            .attr('id', function(d) {
                return 'gnode_' + d.id;
            })
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));

        function dragstarted(d) {
            if(!d3.event.active) {
                THAT.simulation.alphaTarget(0.1).restart();
            }
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function dragended(d) {
            if(!d3.event.active) THAT.simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        this.nodes = this.gnodes.append('rect')
            .attr('width', function(d) {
                return d.width;
            })
            .attr('height', function(d) {
                return d.height;
            })
            .style('opacity', 0.5)
            .style('fill', nodeColor)
            .on('click', function(d) {
                console.log(d);
                d3.select('#to_merge').property('value', d.cluster);
                if(THAT.vars.highlighted) {
                    THAT.resetOpacity();
                } else {
                    // nodes that are reachable with only "has" or "is" edges
                    var set = THAT.hasIsDfs(d);
                    // highlight links/endges that goes to/out of nodes from set
                    THAT.glinks.style('opacity', 0.1);
                    graph.links.forEach(function(d) {
                        var glink = d3.select('#glink_' + d.index);
                        if(set.has(d.source.id) || set.has(d.target.id)) {
                            glink.style('opacity', 1);
                        }
                    });
                    // highlight nodes from set
                    THAT.gnodes.style('opacity', 0.1);
                    THAT.selectById(THAT.nodes, set).each(function(d) {
                        d3.select(this.parentNode).style('opacity', 1);
                    });
                    // highlight nodes, that can reach node from set with only
                    // one "access" edge
                    var sshset = THAT.accessDfs(set);
                    THAT.selectById(THAT.nodes, sshset).each(function(d) {
                        d3.select(this)
                            .style('stroke', 'black')
                            .style('stroke-width', 1)
                        d3.select(this.parentNode)
                            .style('opacity', 1);
                    });
                }
                THAT.vars.highlighted = !THAT.vars.highlighted;
            })
            .on('mouseover', function(d) {
                /* Show node's full text.*/
                d3.select(this.parentNode).select('text')
                    .attr('old_text', function(d) {
                        return this.textContent;
                    })
                    .text(d.value);
                d3.select(this).attr('width', function(d){
                    return (d.value.length * 10 + 2) / THAT.oldScale;
                });
                d3.select(this.parentNode)
                    .attr('mouseover', '');
            })
            .on('mouseout', function(d) {
                /* Reset node's text to initial value. */
                d3.select(this.parentNode).select('text')
                    .text(function(d) {
                        return d3.select(this).attr('old_text');
                    });

                d3.select(this).attr('width', function(d){
                    var length = Math.min(THAT.vars.textLength, d.value.length);
                    return (length * 10 + 2) / THAT.oldScale;
                });
                d3.select(this.parentNode)
                    .attr('mouseover', null);
            })

        ;
        this.nodeLabels = this.gnodes.append('text')
            .style('font-size', THAT.vars.fontSize)
            .style('font-family', 'monospace')
            .style('pointer-events', 'none')
            .text(function(d) {
                /* Makes sure the node's text is not too long. */
                var text = d.value;
                if(text.length <= THAT.vars.textLength) {
                    return text;
                } else {
                    return text.slice(0, THAT.vars.textLength - 3) + '...';
                }
            })
            .style('fill', 'black');
    }

    Map.prototype.filterEvents = function(fromTime, toTime) {
        /* Remove edges that did not happen between  fromTime and toTime.
         * Note that other methods have to be called for this to have actual
         * effect.
         */
        var newLinks = new Array();
        var THAT = this;
        this.backupData.links.forEach(function(d) {
            var newEvents = new Array();
            d.events.forEach(function(e) {
                if(e.timestamp >= fromTime && e.timestamp <= toTime) {
                    newEvents.push(e);
                }
            });
            if(newEvents.length > 0) {
                d.events = newEvents;
                newLinks.push(d);
            }
        });
        this.graph.links = newLinks;
    }

    Map.prototype.setFilter = function(fromTime, toTime) {
        /* Sets filter and triggers and ensures proper drawing of the graph. */

        this.filterEvents(fromTime, toTime);
        // this must be done because some links maybe filtered out.
        this.setForces();
        this.setElements();
        // this will restore zoom level as before.
        this.zoomed();
        this.simulation.alphaTarget(0.01).restart();
    }


    Map.prototype.clusterRoutine = function(cluster_id){
        var THAT = this;
        this.gnodes.style('visibility', function(d){
            if(THAT.merged.has(d.cluster) && d.cluster != d.id){
                return 'hidden';
            } else{
                return 'visible';
            }
        });
        this.linkLabels.style('visibility', function(d){
            if(THAT.getRealTarget(d.source) == THAT.getRealTarget(d.target)){
                return 'hidden';
            } else{
                return 'visible';
            }
        });
        this.tick();
    }

    Map.prototype.merge = function(cluster_id){
        /* Merge nodes in given cluster. */
        cluster_id = parseInt(cluster_id);
        // mark cluster a merged
        this.merged.add(cluster_id);
        this.clusterRoutine();
    }

    Map.prototype.expand = function(cluster_id){
        /* Merge nodes in given cluster. */
        cluster_id = parseInt(cluster_id);
        // mark cluster a merged
        if(this.merged.has(cluster_id)){
            this.merged.delete(cluster_id);
        }
        this.clusterRoutine();
    }

    Map.prototype.render = function(data, element) {
        /* Renders actual graph based on data in element. */
        this.vars = { // variables that needs to be accessed in other methods
            linkWidth: 4,
            fontSize: 15,
            textLength: 20,
            margin: {
                top: 50,
                right: 75,
                bottom: 0,
                left: 40
            },
            highlighted: false
        };
        var THAT = this;
        this.height = 1100;
        this.width = 1200;
        this.simulation;
        this.element = element;

        this.setData(data);
        this.setForces();

        graph = this.graph;
        var minTimestamp = 2439118792937500;
        var maxTimestamp = 0;

        graph.links.forEach(function(link) {
            link.events.forEach(function(e) {
                minTimestamp = Math.min(minTimestamp, e.timestamp);
                maxTimestamp = Math.max(maxTimestamp, e.timestamp);
            })
        })

        graph.nodes.forEach(function(d) {
            d.height = 20;
            d.width = Math.min(THAT.vars.textLength, d.value.length) * 10 + 2;
        });

        this.timelineHolder = d3.select(element).append('p');

        var fromTimeInput = this.timelineHolder.append('input')
            .attr('type', 'number')
            .attr('id', 'from_time')
            .attr('step', 1000000*60*60*24)
            .attr('value', minTimestamp);

        var toTimeInput = this.timelineHolder.append('input')
            .attr('type', 'number')
            .attr('id', 'to_time')
            .attr('step', 1000000*60*60*24)
            .attr('value', maxTimestamp);

        this.timelineHolder.append('button')
            .attr('type', 'button')
            .attr('id', 'filter_button')
            .text('Filter')
            .on('click', function() {
                var fromTime = fromTimeInput.property('value');
                var toTime = toTimeInput.property('value');
                THAT.setFilter(fromTime, toTime);
            });

        this.timelineHolder.append('button')
            .attr('type', 'button')
            .attr('id', 'reset_filter_button')
            .text('Reset')
            .on('click', function() {
                var fromTime = fromTimeInput.property('value');
                var toTime = toTimeInput.property('value');
                THAT.setFilter(minTimestamp, maxTimestamp);
                fromTimeInput.property('value', minTimestamp);
                toTimeInput.property('value', maxTimestamp);
            });

        var MergeInput = this.timelineHolder.append('input')
            .attr('type', 'number')
            .attr('id', 'to_merge');

        this.timelineHolder.append('button')
            .attr('type', 'button')
            .text('Merge')
            .on('click', function(){
                var cluster_id = MergeInput.property('value');
                THAT.merge(cluster_id);
            })

        this.timelineHolder.append('button')
            .attr('type', 'button')
            .text('Expand')
            .on('click', function(){
                var cluster_id = MergeInput.property('value');
                THAT.expand(cluster_id);
            })

        this.timelineHolder.append('button')
            .attr('type', 'button')
            .text('Merge All')
            .on('click', function(){
                THAT.graph.nodes.forEach(function(d){
                    THAT.merge(d.cluster);
                })
            })

        this.timelineHolder.append('button')
            .attr('type', 'button')
            .attr('id', 'merge_button')
            .text('Expand All')
            .on('click', function(){
                THAT.graph.nodes.forEach(function(d){
                    THAT.expand(d.cluster);
                })
            })


        this.timelineHolder.append('button')
            .attr('type', 'button')
            .text('Stop')
            .on('click', function(){THAT.simulation.stop();})

        this.timelineHolder.append('button')
            .attr('type', 'button')
            .text('Restart')
            .on('click', function(){THAT.simulation.restart();})

        d3.select(element).select('svg').remove();
        this.svg = d3.select(element).append('svg')
            .attr('width', THAT.width)
            .attr('height', THAT.height);


        this.holder = this.svg.append('g');

        this.svg.append('svg:defs').append('svg:marker')
            .attr('id', 'mid-arrow')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', -10)
            .attr('markerWidth', 3)
            .attr('markerHeight', 3)
            .attr('orient', 'auto')
            .append('svg:path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#000');

        this.oldScale = 1;
        this.svg.call(d3.zoom()
            .scaleExtent([1 / 5, 20])
            .on('zoom', function() {
                if(typeof THAT.transform != 'undefined'){
                    THAT.oldScale = THAT.transform.k;
                }
                THAT.transform = d3.event.transform;
                THAT.zoomed()
            }));

        this.setElements();

        this.simulation.restart();

        // dictionary of merged clusters.
        this.merged = new Set();

        // adjacency list representation of graph
        this.G = new Array(graph.nodes.length);
        for(var i = 0; i < graph.nodes.length; i++) {
            this.G[i] = new Array();
        }
        for(var i = 0; i < graph.links.length; i++) {
            var link = graph.links[i];
            this.G[link.source.id].push(link);
            this.G[link.target.id].push(link);
        }
    };
    Map.prototype.selectById = function(selection, idSet) {
        /* Helper function to select multiple elements by their data ids.*/
        return selection.filter(function(d) {
            return idSet.has(d.id);
        });
    }

    Map.prototype.resetOpacity = function() {
        /* Set opacity of elements to their initial value. */
        this.nodes.style('stroke-width', 0)
        this.glinks.style('opacity', 1);
        this.gnodes.style('opacity', 1);
    }

    Map.prototype.zoomed = function() {
        /* Handles zoom event*/
        var THAT = this;
        if(typeof THAT.transform == 'undefined') {
            return;
        }
        THAT.holder.attr('transform', THAT.transform);
        var newFontSize = THAT.vars.fontSize / THAT.transform.k;
        THAT.nodeLabels.style('font-size', newFontSize);
        THAT.linkLabels.style('font-size', newFontSize);
        THAT.nodes.attr('width', function(d) {
                return d.width / THAT.transform.k
            })
            .attr('height', function(d) {
                return d.height / THAT.transform.k
            })
            .attr('zoom', THAT.transform.k);
        THAT.links.attr('stroke-width', function(){
            return THAT.vars.linkWidth / THAT.transform.k ;
        });
        this.tick(); //because transform is broken with text
    }

    Map.prototype.hasIsDfs = function(d) {
        /* Finds all nodes that are reachable from d only through 'has' and
         * 'is' links/edges. *
         * d can be array of nodes or one node.
         */
        var THAT = this;
        var done = new Set();
        var linkTypes = ['has', 'is']
        var dfs = function(node) {
            if(done.has(node)) return;
            done.add(node);
            for(var i = 0; i < THAT.G[node].length; i++) {
                var link = THAT.G[node][i];
                if(linkTypes.indexOf(link.type) !== -1) {
                    dfs(link.source.id);
                    dfs(link.target.id);
                }
            }
        }
        if(d instanceof Array) {
            for(var i = 0; i < d.length; i++) {
                dfs(d[i].id);
            }
        } else {
            dfs(d.id);
        }
        return done;
    }

    Map.prototype.accessDfs = function(d) {
        var done = new Set();
        d = Array.from(d);
        for(var i = 0; i < d.length; i++) {
            for(var j = 0; j < this.G[d[i]].length; j++) {
                var link = this.G[d[i]][j];

                if(link.type == 'access') {
                    done.add(link.source.id);
                    done.add(link.target.id);
                }
            }
        }
        for(var i = 0; i < d.length; i++) {
            done.delete(d[i]);
        }
        return done;
    }

    Map.prototype.getRealTarget = function(node){
        if(this.merged.has(node.cluster)){
            return this.graph.nodes[node.cluster];
        } else {
            return node;
        }
        return node;
    }


    Map.prototype.tick = function() {
        /* Handles one tick of simulation. */
        var THAT = this;
        // using quadtree for fast collision detection.
        var q = d3.quadtree()
            .x(function(d) {
                return d.x;
            })
            .y(function(d) {
                return d.y;
            })
            .addAll(this.graph.nodes);

        for(var i = 0; i < this.graph.nodes.length; i++) {
            // visit every node and check for collisions
            q.visit(collide(this.graph.nodes[i], this.oldScale));
        }

        // moving links
        this.links
            .attr('x1', function(d) {
                return THAT.getRealTarget(d.source).x;
            })
            .attr('y1', function(d) {
                return THAT.getRealTarget(d.source).y;
            })
            .attr('x2', function(d) {
                return THAT.getRealTarget(d.target).x;
            })
            .attr('y2', function(d) {
                return THAT.getRealTarget(d.target).y;
            });
        // moving nodes
        this.nodes
            .attr('x', function(d) {
                return d.x;
            })
            .attr('y', function(d) {
                return d.y;
            });
        // moving node labels
        this.nodeLabels
            .attr('x', function(d) {
                var rect = d3.select(this.parentNode).select('rect');
                var rectWidth = rect.attr('width');
                return d.x + rectWidth * 0.03;
            })
            .attr('y', function(d) {
                var rect = d3.select(this.parentNode).select('rect');
                var rectHeight = rect.attr('height');
                return d.y + rectHeight * 0.85;
            });
        // moving link labels
        this.linkLabels
            .attr('x', function(d) {
                var realSource = THAT.getRealTarget(d.source);
                var realTarget = THAT.getRealTarget(d.target);
                return ( realSource.x + realTarget.x ) / 2;
            })
            .attr('y', function(d) {
                var realSource = THAT.getRealTarget(d.source);
                var realTarget = THAT.getRealTarget(d.target);
                return(realSource.y + realTarget.y) / 2;
            });

    }


    function collide(node, scale) {
        scale = 1;
        /* Returns visitor that detects and resolves collisions with node.*/
        var nxPadding = node.width * 0.02 / scale,
            nyPadding = node.height * 0.1 / scale,
            nx1 = node.x - nxPadding,
            ny1 = node.y - nyPadding,
            nx2 = node.x + node.width / scale + nxPadding,
            ny2 = node.y + node.height / scale + nyPadding,
            ncx = (nx1 + nx2) / 2,
            ncy = (ny1 + ny2) / 2;


        return function(tree, x1, y1, x2, y2) {
            /* Gets subguadtree and current bounding box.
             * Determines if this bounding box needs to be considered.
             * In case the tree contains only one node, resolves collision with
             * this node.
             */
            // expand the bounding box
            // TODO redo
            x1 -= node.width / scale + nxPadding;
            y1 -= node.height / scale + nyPadding;
            x2 += node.width / scale + nxPadding;
            y2 += node.height / scale + nyPadding;
            // initialize  variables for geometric computations
            var left = Math.min(x1, nx1, x2, nx2),
                right = Math.max(x1, nx1, x2, nx2),
                up = Math.min(y1, ny1, y2, ny2),
                down = Math.max(y1, ny1, y2, ny2),
                xSize = (x2 - x1) + (nx2 - nx1),
                ySize = (y2 - y1) + (ny2 - ny1),
                xOverlap = xSize - (right - left),
                yOverlap = ySize - (down - up);

            // check is node overlaps with the bounding box
            if(xOverlap > 0 && yOverlap > 0) {
                if('data' in tree && (tree.data !== node)) {
                    // we are in subtree that represents one node
                    var point = tree.data;
                    // we need to exactly determine now much two nodes overlap
                    var pxPadding = point.width*0.02 / scale,
                        pyPadding = point.height*0.02 / scale,
                        px1 = point.x - pxPadding,
                        py1 = point.y - pyPadding,
                        px2 = point.x + point.width / scale + pxPadding,
                        py2 = point.y + point.height / scale + pyPadding,
                        pcx = (px1 + px2) / 2,
                        pcy = (py1 + py2) / 2;

                    var dx = ncx - pcx,
                        dy = ncy - pcy,
                        xSpacing = ((px2 - px1) + (nx2 - nx1)) / 2,
                        ySpacing = ((py2 - py1) + (ny2 - ny1)) / 2,
                        absX = Math.abs(dx),
                        absY = Math.abs(dy),
                        l,
                        lx,
                        ly;

                    if(absX < xSpacing && absY < ySpacing) {
                        l = Math.sqrt(dx * dx + dy * dy);
                        lx = (absX - xSpacing) / l;
                        ly = (absY - ySpacing) / l;

                        // move only in one dimension
                        if(Math.abs(lx) > Math.abs(ly)) {
                            lx = 0;
                        } else {
                            ly = 0;
                        }
                        dx *= lx;
                        node.x -= dx;
                        dy *= ly;
                        node.y -= dy;
                        point.x += dx;
                        point.y += dy;
                        return true;
                    }
                }
                return false;
            } else {
                return true;
            }
        };
    }

    function filteredManyBody(){
        var force = d3.forceManyBody();
        var oldInitialize = force.initialize;
        force.initialize = function(nodes){
            var filtered = nodes.filter(function(d){
                return d.type == 'machine_name' || d.type == 'machine_ip';
            });
            oldInitialize(filtered);
        }
        return force;
    }

    function nodeColor(node) {
        var maper = {
            'machine_name': d3.schemeCategory20[1],
            'ip': d3.schemeCategory20[3],
            'user_name': d3.schemeCategory20[5],
            'user_id': d3.schemeCategory20[7]
        }
        if(node.type in maper) {
            return maper[node.type];
        } else {
            return d3.color('orange');
        }
    }

    function linkStrength(link) {
        var maper = {
            'has': 1,
            'is': 1,
            'access': 0.1,
        }
        return maper[link.type];
        if(link.type in maper) {
            return maper[link.type];
        } else {
            return 1;
        }
    }

    function linkDistance(link) {
        var maper = {
            'has': 10,
            'is': 10,
            'access': 300,
        }
        return maper[link.type];
        if(link.type in maper) {
            return maper[link.type];
        } else {
            return 200;
        }
    }

    function linkColor(link) {
        var maper = {
            'is': d3.color('red'),
            'has': d3.color('blue'),
            'access': d3.color('green'),
        }
        if(link.type in maper) {
            return maper[link.type];
        } else {
            return d3.color('orange');
        }
    }

    var exports = {}
    exports.Map = Map;
    return exports;
}());
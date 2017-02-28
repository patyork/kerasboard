/**
 * Created by Pat York on 2/28/2017.
 */

angular.module('kerasboard.monitor', ['ngWebSocket', 'highcharts-ng', 'gridstack-angular'])
    .factory('MonitorFactory', function($websocket) {
        // Open a WebSocket connection
        var dataStream = $websocket('ws://' + window.location.host + '/ws'); // + '/id=2&test=5'

        var collection = [];
        var datum = {labels: [], values:[]};
        var datum2 = {val:[]};
        dataStream.onMessage(function(message) {
            parsed = JSON.parse(message.data);

            if (parsed.constructor === Array){
                toadd_l = [];
                toadd_v = [];
                for (a in parsed){

                    tmp = JSON.parse(parsed[a]);

                    toadd_l.push(tmp.id);
                    toadd_v.push(tmp.value);
                }
                datum.labels = (datum.labels.concat(toadd_l)).slice(-10);
                datum.values = (datum.values.concat(toadd_v)).slice(-10);

                datum2.val = [].concat(toadd_v)

            }
            else {
                datum.labels.push(parsed.id);
                datum.values.push(parsed.value);

                datum2.val = [JSON.parse(parsed.value)];

            }
        });

        var methods = {
            collection: collection,
            datum: datum,
            datum2: datum2,
            get: function() {
                dataStream.send(JSON.stringify({ action: 'get' }));
            }
        };

        return methods;
    })
    .controller('MonitorController', function ($scope, MonitorFactory, $log) {
        $scope.monitorFactory = MonitorFactory;


        $scope.title = 'No Model'

        // Ugly, but required in Chrome to prevent WebSocket message dropping in priority
        window.onwheel = function(){
            window.scrollBy(0, window.event.deltaY *.5);
            return false;   // capture
        };

        $scope.options = {
            cellHeight: 40,
            verticalMargin: 10,
            height: 50,
            width: 12,
            //float: true
        };
        $scope.default_widgets = [
            { x:0, y:0, width:4, height: 6, id: 'file'},
            { x:0, y:6, width:4, height: 6, id: 'engravingSettings'},
            { x:0, y:12, width:4, height: 7, id: 'laserSettings'},
            { x:0, y:22, width:4, height: 5},

            { x:10, y:0, width:2, height: 4, id: 'machineSettings'},
            { x:10, y:4, width:2, height: 4, id: 'preprocSettings'},
            { x:10, y:8, width:2, height: 3, id: 'stats'},
            { x:10, y:11, width:2, height: 4, id: 'process'},

        ];
        $scope.gridstacker = null;
        if(localStorage.getItem('last_layout')) {
            $scope.widgets = angular.fromJson(localStorage.getItem('last_layout'));
        }
        else {
            $scope.widgets = $scope.default_widgets;
        }
        $scope.reset_layout = function() {
            $scope.widgets = $scope.default_widgets;
            $scope.saveLayout();
        };
        //$scope.widgets = $scope.default_widgets; //# todo remove
        $scope.saveLayout = function() {
            localStorage.setItem('last_layout', angular.toJson($scope.widgets));
        };
        $scope.addWidget = function() {
            var newWidget = { x:0, y:0, width:1, height:1 };
            $scope.widgets.push(newWidget);
        };
        $scope.removeWidget = function(w) {
            var index = $scope.widgets.indexOf(w);
            $scope.widgets.splice(index, 1);
        };
        $scope.onChange = function(event, items) {
            $scope.reflow();
        };
        $scope.onDragStart = function(event, ui) {
        };
        $scope.onDragStop = function(event, ui) {
            $scope.saveLayout();
        };
        $scope.onResizeStart = function(event, ui) {
        };
        $scope.onResizeStop = function(event, ui) {
            $scope.saveLayout();
            $scope.reflow();
        };
        $scope.onItemAdded = function(item) {
            $scope.saveLayout();
        };
        $scope.onItemRemoved = function(item) {
            $scope.saveLayout();
        };



        function clone(obj) {
            var copy;
            // Handle the 3 simple types, and null or undefined
            if (null == obj || "object" != typeof obj) return obj;

            // Handle Date
            if (obj instanceof Date) {
                copy = new Date();
                copy.setTime(obj.getTime());
                return copy;
            }

            // Handle Array
            if (obj instanceof Array) {
                copy = [];
                for (var i = 0, len = obj.length; i < len; i++) {
                    copy[i] = clone(obj[i]);
                }
                return copy;
            }

            // Handle Object
            if (obj instanceof Object) {
                copy = {};
                for (var attr in obj) {
                    if (obj.hasOwnProperty(attr)) copy[attr] = clone(obj[attr]);
                }
                return copy;
            }

            throw new Error("Unable to copy obj! Its type isn't supported.");
        }

        $scope.$watch('monitorFactory', function(new_val, old_val){
            // Main
            var seriesArray = $scope.chartConfig.series;
            seriesArray[1].data = seriesArray[1].data.concat(new_val.datum2.val);

            // Middle
            var seriesArray = $scope.chartConfig2.series;
            seriesArray[1].data = seriesArray[1].data.concat(new_val.datum2.val).slice(-1000);

            // Last
            var seriesArray = $scope.chartConfig3.series;
            seriesArray[1].data = seriesArray[1].data.concat(new_val.datum2.val).slice(-100);
        }, true);


        $scope.chartSeries = [
            {"name": "Loss", "data": [], id: 'loss'},
            {"name": "Metric", "data": [], connectNulls: true, id: 'metric'},
        ];
        $scope.chartConfig = {
            exporting: {
                chartOptions: { // specific options for the exported image
                    plotOptions: {
                        series: {
                            dataLabels: {
                                enabled: false
                            }
                        }
                    }
                },
                fallbackToExportServer: false
            },
            chart: {
                type: 'line',
                height: 800,        // Set to a large default value; will change to Gridstack container size.
                animation: false    //doesn't actually turn it off, but what can you do. Thought that counts.
            },
            plotOptions: {
                series: {
                    stacking: '',
                }
            },
            series: $scope.chartSeries,
            title: {
                text: 'Epoch'
            }
        };

        $scope.chartConfig2 = clone($scope.chartConfig);
        $scope.chartConfig2.title.text = 'Last 1000 Batches (Averaged over 10)';
        $scope.chartConfig3 = clone($scope.chartConfig);
        $scope.chartConfig3.title.text = 'Last 100 Batches';

        $scope.charts = [$scope.chartConfig, $scope.chartConfig2, $scope.chartConfig3]


        $scope.reflow = function () {
            angular.forEach($scope.charts, function(value, key) {
                value.chart.height = value.getChartObj().container.parentElement.parentElement.parentElement.clientHeight;
                value.chart.width = value.getChartObj().container.parentElement.parentElement.parentElement.clientWidth;
                value.getChartObj().reflow()
            });
        };
    });
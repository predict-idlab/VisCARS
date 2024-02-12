class EnrichedCall {

    constructor(title, data) {
        this.title = title;
        this.data = data;
    }

    getHTML() {
        const latestObservation = this.data[0];

        const container = document.createElement("div");
        container.style.padding = '10px 10px 10px 10px';

        const title_ = document.createElement("p");
        // title_.style.color = '#333333';
        title_.style.fontSize = '1.4em';
        title_.style.fontWeight = 'bold';
        title_.style.marginBottom = '10px'
        title_.className = 'text-center';
        title_.innerText = this.title;
        container.appendChild(title_);

        const json = typeof latestObservation === "object" ? latestObservation[1] : JSON.parse(latestObservation[1]);
        const payload = typeof json.value === "string" ? JSON.parse(json.value) : JSON.parse(JSON.stringify(json.value));
        let sortedPayload = [];
        for (const key in payload) {
            sortedPayload.push([key, payload[key]]);
        }
        sortedPayload.sort();

        const table = document.createElement("table");
        table.classList.add("table");

        sortedPayload.forEach(kv => {
            const key = kv[0];
            const content = kv[1];

            const row = document.createElement("tr");
            const header = document.createElement("th");
            header.textContent = key;
            header.setAttribute("scope", "row");
            const value = document.createElement("td");

            if (content instanceof Array) {
                const list = document.createElement("ul");
                content.forEach(x => {
                    const item = document.createElement("li")
                    item.textContent = x;
                    list.appendChild(item);
                });
                value.appendChild(list);
            } else if (typeof (content) == "boolean") {
                const label = document.createElement("i")
                label.className = content ? 'bi bi-check' : 'bi bi-x';
                label.style.color = content ? 'green' : 'red';
                value.appendChild(label);
            } else {
                value.textContent = payload[key];
            }

            row.appendChild(header);
            row.appendChild(value);
            table.appendChild(row);
        });

        container.appendChild(table);
        const timestamp = document.createElement("span");
        timestamp.className = 'small float-right';
        timestamp.innerHTML = '<b>Last updated: </b>' + new Date(latestObservation[0]);
        container.appendChild(timestamp);

        return container.outerHTML;
    }
}

class SolidGauge {
    constructor(title, data, unit, min, max, thresholds, thresholdColors) {
        this.title = title;
        this.data = data;
        this.unit = unit;
        this.min = min;
        this.max = max;
        if (thresholds) {
            this.thresholds = thresholds.map((k, i) => [k, thresholdColors[i]]);
        } else {
            this.thresholds = []
        }
    }

    getChartOptions() {
        return {
            chart: {
                type: 'solidgauge',
                plotBorderWidth: 0,
                plotShadow: false,
                styledMode: false
            },

            title: {
                text: this.title,
                y: 40,
                style: {
                    fontWeight: 'bold',
                    fontSize: '1.4em'
                }
            },

            pane: {
                center: ['50%', '85%'],
                size: '100%',
                startAngle: -90,
                endAngle: 90,
                background: {
                    backgroundColor: Highcharts.defaultOptions.legend.backgroundColor || '#EEE',
                    innerRadius: '60%',
                    outerRadius: '100%',
                    shape: 'arc'
                }
            },

            credits: {
                enabled: false,
            },

            tooltip: {
                enabled: false
            },

            series: [{
                name: this.title,
                data: this.data,
                tooltip: {
                    valueSuffix: ` ${this.unit}`
                },
                dataLabels: {
                    format:
                        '<div style="text-align:center">' +
                        '<span class="highcharts-dashboards-component-kpi-value">{y}</span><br/>' +
                        `<span class="highcharts-dashboards-component-kpi-subtitle">${this.unit}</span>` +
                        '</div>'
                }
            }],

            yAxis: {
                min: this.min,
                max: this.max,
                stops: this.thresholds,
                lineWidth: 0,
                minorTickInterval: null,
                tickWidth: 0,
                tickAmount: 2,
                labels: {
                    y: 16
                }
            },

            plotOptions: {
                solidgauge: {
                    dataLabels: {
                        y: 5,
                        borderWidth: 0,
                        useHTML: true
                    }
                }
            },
        }
    }
}

class Thermometer {

    draw(containerElementId, title, data, unit) {

        // Get the reference node
        this.container = document.getElementById(containerElementId);

        // <div id="container" style="width: 80px; height: 400px; margin: 0 auto"></div>
        var container = document.createElement('div');
        container.setAttribute('id', 'container');
        container.setAttribute('width', '80');
        container.setAttribute('height', '400');
        container.setAttribute('margin', '0 auto');

        this.container.appendChild(container);

        // <svg class='svg-background' width= 80 height=500>
        //     <circle cx='36' cy='412' r='20'></circle>
        //     <path d="M 22 20 L 22 400 M 50 400L 50 20 C 50 0 22 0  22 20"></path>
        // </svg>

        // Create new elements
        var circle = document.createElement('circle');
        circle.setAttribute('cx', '36');
        circle.setAttribute('cy', '412');
        circle.setAttribute('r', '20');

        var path = document.createElement('path');
        path.setAttribute('d', 'M 22 20 L 22 400 M 50 400L 50 20 C 50 0 22 0  22 20');

        var svg = document.createElement('svg');
        svg.classList.add('svg-background');
        svg.setAttribute('width', '80');
        svg.setAttribute('height', '500');

        svg.appendChild(circle);
        svg.appendChild(path);

        this.container.appendChild(svg);

        // Highcharts.setOptions({
        //     global: {
        //         useUTC: false
        //     }
        // });

        const chartOptions = {

            chart: {
                type: 'column',
                backgroundColor: 'transparent',
                hover: {
                    backgroundColor: 'transparent'
                }
            },
            exporting: {
                enabled: false
            },
            credits: {
                enabled: false
            },
            title: {
                text: '',
            },
            pane: {
                backgroundColor: 'transparent',
            },
            xAxis: {
                categories: [
                    ''
                ],
                tickWidth: 0,
                gridLineWidth: 0,
                minorGridLineWidth: 0,
                lineColor: 'transparent',
                crosshair: true,
                labels: {
                    enabled: false
                },
            },
            yAxis: {
                title: {
                    text: unit
                },
                labels: {
                    enabled: true,
                    x: 37,
                    style: {
                        color: '#B3B3B3'
                    }
                },
                gridLineWidth: 0,
                minorGridLineWidth: 0,
                lineColor: 'transparent',
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                column: {
                    borderWidth: 0
                },
                series: {
                    pointWidth: 20
                }
            },
            series: [{
                name: title,
                data: data,
                tooltip: {
                    valueSuffix: ` ${unit}`
                },
                states: {
                    hover: {
                        borderColor: 'transparent',
                        brightness: 0
                    }
            },
            }]

        };

        this.chart = Highcharts.chart(containerElementId, chartOptions);
    }

    /**
     * Update the chart with a new observation.
     * @param newObservations: an array of newObservations made by a sensor,
     * consisting of items that have the following array format: [timestamp, observation],
     * with timestamp being the time at which the observation was made, in integer format, for example: 1531475536122.
     */
    update(newObservations) {
        //console.log(newObservations)
    }


    /**
     * Destroy the chart: make the browser release all resources that were in use to draw the chart.
     */
    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
    }

}

class TimeSeriesLineChart {

    constructor(title, data, unit, min, max, thresholds, thresholdColors) {
        this.title = title;
        this.data = data;
        this.unit = unit;
        console.log(this.data);
        if (thresholds) {
            this.thresholds = thresholds.map((k, i) => ({value: k, className: thresholdColors[i]}));
        } else {
            this.thresholds = []
        }
    }

    draw(elementId) {
        this.chart = new Highcharts.Chart(elementId, this.getChartOptions());
    }

    getChartOptions() {
        return {
            chart: {},

            title: {
                text: this.title,
                style: {
                    fontWeight: 'bold',
                    fontSize: '1.4em'
                }
            },

            xAxis: {
                type: 'datetime',
                title: {
                    text: 'Time'
                },
                ordinal: false // Draw time slots for which there is no data (https://github.com/highcharts/highcharts/issues/8670).
            },
            yAxis: {
                title: {
                    text: this.unit
                }
            },

            exporting: {
                enabled: false
            },

            credits: {
                enabled: false
            },

            tooltip: {
                enabled: true
            },

            legend: {
                enabled: false
            },

            series: [{
                name: this.title,
                data: this.data,
                tooltip: {
                    valueDecimals: 1,
                    valueSuffix: ` ${this.unit}`
                },
                zoneAxis: "y",
                zones: this.thresholds
            }],

            plotOptions: {
                line: {
                    marker: {
                        enabled: false
                    }
                },
                series: {
                    label: {
                        enabled: false
                    }
                }
            },
        }
    }
}
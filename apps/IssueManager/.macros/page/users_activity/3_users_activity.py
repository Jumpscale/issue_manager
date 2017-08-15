from issuemanagerlib import issuemanager

def main(j, args, params, tags, tasklet):
    page = args.page

    macrostr = args.macrostr.strip().strip('{{').strip('}}')
    tags = j.data.tags.getObject(macrostr, keepcase=True)
    tags = tags.getDict()
    tags.pop(args.macro)

    activity = issuemanager.getActivityCollectionFromDB()

    page.addJS("/IssueManager/.files/js/d3/3.5.6/d3.min.js")
    page.addJS("/IssueManager/.files/js/cal-heatmap/3.3.10/cal-heatmap.min.js")
    page.addCSS("/IssueManager/.files/css/cal-heatmap/3.3.10/cal-heatmap.css")

    out1 = "</p><ul>"
    out2 = ""

    activity_info = {}
    for act in activity.find(**tags):
        activity_info.setdefault(act.dbobj.name, [])
        activity_info[act.dbobj.name].append(act.dbobj.timestamp)

    for name, timestamps in activity_info.items():
        userdata = ['"%s": %s' % (timestamp, 1) for timestamp in timestamps]
        start = min(timestamps)
        start = j.data.time.formatTime(start, formatstr="%Y, %m")
        data = ', '.join(userdata)
        name_escaped = name.replace('.', '').replace(' ', '')
        out1 += '<li><a href="#{0}">{0}</a></br></li>'.format(name)

        out2 += """
            <h3><a name="{name}">{name}</a></h3>
            <div id="cal-heatmap-{name_escaped}"></div>
                <script type="text/javascript">
                    var data={{{data}}};
                    var calheatmap= new CalHeatMap();
                    calheatmap.init({{
                            itemSelector: '#cal-heatmap-{name_escaped}',
                            domain: 'month',
                            data: data,
                            start: new Date({start}),
                            considerMissingDataAsZero: false,
                            dataType: "json",
                            label: {{
                                position: "top"
                            }}
                        }});
                </script>

            </br></br>
            """.format(name=name, data=data, start=start, name_escaped=name_escaped)
    out = out1 + '</ul>' + out2 + '</p>'
    page.addHTML(out)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True

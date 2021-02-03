/*
A KBase module: kb_virmatcher
*/

module kb_virmatcher {

    typedef string obj_ref;

    typedef structure {

        string workspace_name;
        obj_ref viral_genomes;
        obj_ref host_genomes;
        string report_name;
        string report_ref;

    } InParams;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */

    typedef structure{
        string report_name;
        string report ref;
    } ReportResults;

    funcdef run_kb_virmatcher(InParams params)
        returns (ReportResults report_output) authentication required;

};

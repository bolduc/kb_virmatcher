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
    funcdef run_kb_virmatcher(InParams params)
        returns () authentication required;

};

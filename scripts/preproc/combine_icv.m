clear all;

proj_dir = pwd;
data_dir = fullfile('/indirect', 'proc_data1', 'brainage', 'Cimbi_database');

for tracer = {'Altanserin', 'Cimbi36'}
    
    % Load subjects
    dataset = tracer{1};
    tbl = readtable(fullfile(data_dir, dataset, 'worklist_get_files.xlsx'),'VariableNamingRule', 'preserve');
       
    if strcmp(dataset, 'Altanserin')
        sub_id_col = 'CIMBI ID';
        pet_id_col = 'ALT ID';
        mr_id_col = 'MR log number used for this ALT PET analysis - T1';
    end

    if strcmp(dataset, 'Cimbi36')
        sub_id_col = 'CIMBI ID';
        pet_id_col = 'Cimbi-36 ID';
        mr_id_col = 'MR log number used for this Cimbi-36 PET analysis - T1';
    end
    
    subjects = tbl.(sub_id_col);
    mr_ids = tbl.(mr_id_col);

    icv_dir = fullfile(data_dir, dataset, 'Output', 'ICV');
    
    results = tbl(:,[string(sub_id_col) string(mr_id_col) string(pet_id_col)]);
    results.icv = zeros(length(subjects),1);
    
    for i = 1:length(subjects)

        subject = int2str(subjects(i));
        mr_id = mr_ids{i};
        
        out_dir = fullfile(icv_dir, ['sub-' subject]);

        % Check if subject is already processed
        icv_file = fullfile(out_dir, 'icv.txt');

        if not(isfile(icv_file))

            disp(['Missing sub-' subject]);

        else
            line = readlines(icv_file);
            pattern = '\d+\.\d+';
            matches = regexp(line, pattern, 'match');
            icv = str2double(matches{1});

            results.icv(i) = icv;
        end   
    end
    % rename columns
    results.Properties.VariableNames = {'subject_id', 'mr_id', 'pet_id', 'icv'};
    % write table 
    writetable(results, fullfile(icv_dir,'icvs.csv'));
end
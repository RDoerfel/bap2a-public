clear all;

run_spm12;

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
    unix(['mkdir -p ' icv_dir]);
    
    parfor i = 1:length(subjects)

        subject = int2str(subjects(i));
        mr_id = mr_ids{i};
        
        out_dir = fullfile(icv_dir, ['sub-' subject]);

        % Check if subject is already processed
        icv_file = fullfile(out_dir, 'icv.txt');

        if not(isfile(icv_file))

            disp(['Processing sub-' subject]);

            % Create output directory
            unix(['mkdir -p ' out_dir]);
            try
                % get mri file
                mri_dir = fullfile(data_dir, dataset, ['CimbiID_'  subject], 'FileLoad');
                nii_file_name = dir(fullfile(mri_dir, '*.nii')).name;
                nii_file_src = fullfile(mri_dir,nii_file_name);
                nii_file_dst = fullfile(out_dir,nii_file_name);

                % copy to new destination
                copyfile(nii_file_src,nii_file_dst)

                % move to subject data folder
                cd(out_dir);

                % run matlabbatch job


                matlabbatch = {};
                matlabbatch{1}.spm.spatial.preproc.channel.vols = {convertStringsToChars(nii_file_dst)};
                matlabbatch{1}.spm.spatial.preproc.channel.biasreg = 0.001;
                matlabbatch{1}.spm.spatial.preproc.channel.biasfwhm = 60;
                matlabbatch{1}.spm.spatial.preproc.channel.write = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(1).tpm = {'/usr/local/nru/spm12/tpm/TPM.nii,1'};
                matlabbatch{1}.spm.spatial.preproc.tissue(1).ngaus = 2;
                matlabbatch{1}.spm.spatial.preproc.tissue(1).native = [1 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(1).warped = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(2).tpm = {'/usr/local/nru/spm12/tpm/TPM.nii,2'};
                matlabbatch{1}.spm.spatial.preproc.tissue(2).ngaus = 2;
                matlabbatch{1}.spm.spatial.preproc.tissue(2).native = [1 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(2).warped = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(3).tpm = {'/usr/local/nru/spm12/tpm/TPM.nii,3'};
                matlabbatch{1}.spm.spatial.preproc.tissue(3).ngaus = 2;
                matlabbatch{1}.spm.spatial.preproc.tissue(3).native = [1 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(3).warped = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(4).tpm = {'/usr/local/nru/spm12/tpm/TPM.nii,4'};
                matlabbatch{1}.spm.spatial.preproc.tissue(4).ngaus = 4;
                matlabbatch{1}.spm.spatial.preproc.tissue(4).native = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(4).warped = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(5).tpm = {'/usr/local/nru/spm12/tpm/TPM.nii,5'};
                matlabbatch{1}.spm.spatial.preproc.tissue(5).ngaus = 4;
                matlabbatch{1}.spm.spatial.preproc.tissue(5).native = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(5).warped = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(6).tpm = {'/usr/local/nru/spm12/tpm/TPM.nii,6'};
                matlabbatch{1}.spm.spatial.preproc.tissue(6).ngaus = 2;
                matlabbatch{1}.spm.spatial.preproc.tissue(6).native = [0 0];
                matlabbatch{1}.spm.spatial.preproc.tissue(6).warped = [0 0];
                matlabbatch{1}.spm.spatial.preproc.warp.mrf = 1;
                matlabbatch{1}.spm.spatial.preproc.warp.cleanup = 1;
                matlabbatch{1}.spm.spatial.preproc.warp.reg = [0 0.001 0.5 0.05 0.2];
                matlabbatch{1}.spm.spatial.preproc.warp.affreg = 'mni';
                matlabbatch{1}.spm.spatial.preproc.warp.fwhm = 0;
                matlabbatch{1}.spm.spatial.preproc.warp.samp = 3;
                matlabbatch{1}.spm.spatial.preproc.warp.write = [0 0];
                matlabbatch{2}.spm.util.tvol.matfiles(1) = {[out_dir filesep erase(nii_file_name,'.nii') '_seg8.mat']};
                matlabbatch{2}.spm.util.tvol.tmax = 3;
                matlabbatch{2}.spm.util.tvol.mask = {'/usr/local/nru/spm12/tpm/mask_ICV.nii,1'};
                matlabbatch{2}.spm.util.tvol.outf = 'tissuevolumes';

                spm('defaults','fmri');
                spm_jobman('initcfg');
                spm_jobman('run',matlabbatch);

                % write out volumes
                csv_file = [out_dir filesep 'tissuevolumes.csv'];
                volumes = readmatrix(csv_file);
                icv = sum(volumes(2:4));
                f = fopen(icv_file,'w');
                fprintf(f,'ICV %f', icv);
                fclose(f);
                
                % remove copied .nii
                delete(nii_file_dst);

            catch err % if there's an error, take notes & move on
                disp(['ERROR: sub-' subject]);
                % remove copied .nii
                continue;
            end
        end

    end
end
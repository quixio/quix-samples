function quix_compiler(function_name, destination_folder, do_zip)
    % quix_compiler Compiles a MATLAB function to Python, builds a wheel, and optionally zips the output.
    % Inputs:
    %   function_name       - Name of the MATLAB function file (e.g., 'myfunc')
    %   destination_folder  - Destination folder for the compiled output (e.g., 'build_output')
    %   do_zip              - (Optional) Boolean flag: zip the output folder? Default = true

    if nargin < 3
        do_zip = true;
    end

    % Define subfolder for mcc output
    out_folder = fullfile(destination_folder, 'out');

    % Step 0: Create folders if they don’t exist
    if ~exist(out_folder, 'dir')
        mkdir(out_folder);
    end

    % Step 1: Compile using mcc into destination_folder/out
    try
        fprintf('Compiling %s.m into %s...\n', function_name, out_folder);
        mcc('-W', ['python:quixmatlab,' function_name], ...
            '-d', out_folder, ...
            [function_name, '.m']);
    catch ME
        error('Compilation failed: %s', ME.message);
    end

    % Step 2: Copy build_wheel.sh to destination_folder
    script_name = 'build_wheel.sh';
    if exist(script_name, 'file') == 2
        try
            copyfile(script_name, destination_folder);
            fprintf('Copied %s to %s.\n', script_name, destination_folder);
        catch ME
            error('Failed to copy script: %s', ME.message);
        end
    else
        warning('%s not found in current directory.\n', script_name);
    end

    % === Step 3: Check if pip is installed, if not, install it ===
    [pip_status, ~] = system('python3 -m pip --version');
    if pip_status ~= 0
        fprintf('pip not found. Installing with get-pip.py...\n');
        system('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py');
        system('python3 get-pip.py');
        delete('get-pip.py');  % Clean up
    else
        fprintf('pip is already installed.\n');
    end

    % === Step 4: Run build_wheel.sh in destination_folder ===
    fprintf('Running build_wheel.sh in %s...\n', destination_folder);
    build_cmd = sprintf('cd "%s" && bash build_wheel.sh', destination_folder);
    build_status = system(build_cmd);
    if build_status ~= 0
        error('build_wheel.sh failed to run correctly.');
    end

    % Step 5: Optionally zip the destination_folder
    if do_zip
        zip_name = [destination_folder, '.zip'];
        try
            zip(zip_name, destination_folder);
            fprintf('Created zip file: %s\n', zip_name);
        catch ME
            error('Failed to create zip: %s', ME.message);
        end
    else
        fprintf('Skipping zipping step as requested.\n');
    end

    fprintf('All tasks completed successfully.\n');
end
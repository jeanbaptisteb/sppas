## List of error messages

Since version 1.9.0, SPPAS introduced a system for internationalization of the
messages. In the same time, a quality and a number was assigned progressively 
to each of them in the packages.
The following indicates the list of error messages that can occur while using 
SPPAS.


#### From "annotations" package

:ERROR 1010: Unknown option with key {key}.

:ERROR 1020: Empty input tier {name}.

:ERROR 1030: Missing input tier. Please read the documentation.

:ERROR 1040: Bad input tier type. Expected time-aligned intervals.

:ERROR 1050: Inconsistency between the number of intervals of the input tiers. Got: {:d} and {:d}.


#### From "utils" package

:ERROR 1210: The directory {dirname} does not exist.

:ERROR 1220: The directory {dirname} does not contain relevant data.


#### From "audiodata" package

:ERROR 2000: No audio file is defined.

:ERROR 2005: Audio type error: not supported file format {extension}.

:ERROR 2010: Opening, reading or writing error.

:ERROR 2015: No data or corrupted data in the audio file {filename}.

:ERROR 2020: {number} is not a right index of channel.

:ERROR 2025: From {value1} to {value2} is not a proper interval.

:ERROR 2050: No channel defined.

:ERROR 2060: Channels have not the same sample width.

:ERROR 2061: Channels have not the same frame rate.

:ERROR 2062: Channels have not the same number of frames.

:ERROR 2070: Invalid sample width {value}.

:ERROR 2080: Invalid frame rate {value}.


#### From "calculus" package

:ERROR 3010: Both vectors p and q must have the same length and must contain probabilities.

:ERROR 3015: Value must range between 0 and 1. Got {:f}.

:ERROR 3016: Probabilities must sum to 1. Got {:f}.

:ERROR 3025: Error while estimating Euclidian distances of rows and columns.

:ERROR 3030: The given data must be defined or must not be empty.

:ERROR 3040: Value {value} is out of range: expected value in range [{min_value},{max_value}].


#### From "plugins" package

:ERROR 4010: Missing plugin configuration file.

:ERROR 4014: Missing section {section_name} in the configuration file.

:ERROR 4016: Missing option {:s} in section {:s} of the configuration file.

:ERROR 4020: Unsupported plugin file type.

:ERROR 4024: Unsupported plugin file type.

:ERROR 4030: A plugin with the same name is already existing in the plugins folder.

:ERROR 4040: No plugin with identifier {plugin_id} is available.

:ERROR 4050: No such plugin folder: {:s}.

:ERROR 4060: A plugin with the same key is already existing or plugin already loaded.

:ERROR 4070: {command_name} is not a valid command on your operating system.

:ERROR 4075: No command was defined for the system: {:s}. Supported systems of this plugin are: {:s}."""

:ERROR 4080: No option with key {:s}.


#### From "resources" package

:ERROR 5005: Encoding error while trying to read the file: {name}.

:ERROR 5010: Error while trying to open and read the file: {name}.

:ERROR 5015: Read file failed at line number {number}: {string}.

:ERROR 5020: The n value of n-grams pattern matching must range [1;{maximum}]. Got {observed}.

:ERROR 5022: The gap value of pattern matching must range [0;{maximum}]. Got {observed}.

:ERROR 5024: The score value of unigrams pattern matching must range [0;1]. Got {observed}.

:ERROR 5030: The dump file can't have the same extension as the ASCII file ({extension}).

:ERROR 5040: The count value must be positive. Got ({count}).


#### From "structs" package

:ERROR 6010: {meta} is not a known meta information.

:ERROR 6020: Unknown resource type: expected file or directory. Got: {string}.

:ERROR 6024: The resource folder {dirname} does not exists.

:ERROR 6028: The language must be "und" or one of the language list. Unknown language {lang}.


#### From "models" package

:ERROR 7010: Expected a {data_name} of type {expected_type}. Got {data_type} instead.

:ERROR 7500: The file {!s:s} contains non UTF-8 characters: {:s}.

:ERROR 7505: Fail formats: unrecognized file format {!s:s}.

:ERROR 7510: Fail formats: the folder {!s:s} does not contain a known model.

:ERROR 7515: No model found or empty model in {!s:s}.

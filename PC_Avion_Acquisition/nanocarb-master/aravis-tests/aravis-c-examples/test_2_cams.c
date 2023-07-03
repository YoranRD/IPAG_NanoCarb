/* SPDX-License-Identifier:Unlicense */

/* Aravis header */

#include <arv.h>

/* Standard headers */

#include <stdlib.h>
#include <stdio.h>
#include <time.h>

int
main (int argc, char **argv)
{
	ArvCamera *camera1;
    ArvCamera *camera2;
	GError *error = NULL;

	ArvDevice *device1;
    ArvDevice *device2;

	int TABSIZE = 1000;

	double tabStart[TABSIZE];
	double tabClose[TABSIZE];
	double tabHeader[TABSIZE];
	double tabData[TABSIZE];
	double tabOthers[TABSIZE];

	/* Connect to the first available camera */
	camera = arv_camera_new (NULL, &error);

	if (ARV_IS_CAMERA (camera)) {
		device = arv_camera_get_device(camera);
		ArvStream *stream;

		printf ("Found camera '%s'\n", arv_camera_get_model_name (camera, NULL));

		/* Get FPS */
		float FPS = arv_device_get_float_feature_value(device, "FrameRate", &error);
    	printf("FPS : %f\n", FPS);

		/* Get IT */
		float IT = arv_device_get_float_feature_value(device, "IntegrationTime", &error);
		printf("IT : %f\n", IT);
		
		/* Set FPS */
		arv_device_set_float_feature_value(device, "FrameRate", 5.0, &error);

		arv_device_set_float_feature_value(device, "IntegrationTime", 2000, &error);

		FPS = arv_device_get_float_feature_value(device, "FrameRate", &error);
    	printf("FPS : %f\n", FPS);


		/* Create the stream object without callback */
		stream = arv_camera_create_stream (camera, NULL, NULL, &error);
		if (ARV_IS_STREAM (stream)) {
			int i;
			size_t payload;

			/* Retrive the payload size for buffer creation */
			payload = arv_camera_get_payload (camera, &error);
			if (error == NULL) {
				/* Insert some buffers in the stream buffer pool */
				for (i = 0; i < 5; i++)
					arv_stream_push_buffer (stream, arv_buffer_new (payload, NULL));
			}

			if (error == NULL)
				/* Start the acquisition */
				arv_camera_start_acquisition (camera, &error);

			struct timespec begin, end, start, stop, startClose, stopClose, b_header, e_header, b_data, e_data, b_others, e_others;

			/* Open file */
            FILE * file;
            file = fopen("test_video.raw", "wb");

			if (error == NULL) {
                /* Skip first header */
                fseek(file, 1024, SEEK_END);

                int img_id = 0;
                
				/* Retrieve n buffers */
				timespec_get(&begin, TIME_UTC);

				for (i = 0; i < TABSIZE; i++) {

					ArvBuffer *buffer;

					buffer = arv_stream_pop_buffer (stream);
					timespec_get(&start, TIME_UTC);	

					if (ARV_IS_BUFFER (buffer)) {
							
						/* Display some informations about the retrieved buffer */
						size_t size;
                        const char* data = arv_buffer_get_data(buffer, &size);

						timespec_get(&b_header, TIME_UTC);
						/* Get Timestamp and write it */
						struct timespec now;
						timespec_get(&now, TIME_UTC);											
						
						struct tm * time = gmtime(&now.tv_sec);

						int year = time->tm_year+1900;
						int month = time->tm_mon+1;
						int day = time->tm_mday;
						int hour = time->tm_hour;
						int min = time->tm_min;
						int sec = time->tm_sec;
						int msec = now.tv_nsec/1.0e6;

                        /* Skip tps */
						fseek(file, 8, SEEK_END);				
						
						fwrite(&year, 2, 1, file);
						fwrite(&month, 2, 1, file);
						fwrite(&day, 2, 1, file);
						fwrite(&hour,2, 1, file);
						fwrite(&min, 2, 1, file);
						fwrite(&sec, 2, 1, file);
						fwrite(&msec, 2, 1 ,file);
						
						/* Frame ID */
						int frame = arv_buffer_get_frame_id(buffer);
						fwrite(&frame, 4, 1, file);
						fwrite(&img_id, 4, 1, file);

						/* T_FPA */
						double T_FPA = arv_device_get_float_feature_value(device, "TemperatureFPA", &error);
						fwrite(&T_FPA, 8, 1, file);

						/* T_Engine */
						double T_Engine = arv_device_get_float_feature_value(device, "TemperatureEngine", &error);
						fwrite(&T_Engine, 8, 1, file);
						

						/* Skip the rest of header to have a 1024 size */
						fseek(file, 978, SEEK_END);

						timespec_get(&e_header, TIME_UTC);
                        
						timespec_get(&b_data, TIME_UTC);
						/* Write Data */
						fwrite(data, size, 1, file);
						timespec_get(&e_data, TIME_UTC);

						timespec_get(&b_others, TIME_UTC);
						/* Don't destroy the buffer, but put it back into the buffer pool */
						arv_stream_push_buffer (stream, buffer);	
						

                        ++img_id;
						//fflush(file);
						timespec_get(&e_others, TIME_UTC);
					}
					timespec_get(&stop, TIME_UTC);
					tabStart[i] = (stop.tv_nsec-start.tv_nsec)/1.0e6;
					tabHeader[i] = (e_header.tv_nsec-b_header.tv_nsec)/1.0e6;
					tabData[i] = (e_data.tv_nsec-b_data.tv_nsec)/1.0e6;
					tabOthers[i] = (e_others.tv_nsec-b_others.tv_nsec)/1.0e6;
				}
			}
            

			timespec_get(&end, TIME_UTC);
			int totalTimeS = (int) end.tv_sec-begin.tv_sec;
			double totalTimeMs = (double)  (end.tv_nsec-begin.tv_nsec)/1.0e9;
			double totalTime = totalTimeS+totalTimeMs;

			timespec_get(&startClose, TIME_UTC);
			fclose(file);
			timespec_get(&stopClose, TIME_UTC);

			int closeTS = (int) stopClose.tv_sec-startClose.tv_sec;
			double closeTMS = (double) (stopClose.tv_nsec-startClose.tv_nsec)/1.0e9;
			double closeT = closeTS+closeTMS;


			printf("MinS : %.2f\n", getMin(tabStart, TABSIZE));
			printf("MaxS : %.2f\n", getMax(tabStart, TABSIZE));
			printf("AvgS : %.2f\n", getAvg(tabStart, TABSIZE));

			printf("MinHeader : %.2f\n", getMin(tabHeader, TABSIZE));
			printf("MaxHeader : %.2f\n", getMax(tabHeader, TABSIZE));
			printf("AvgHeader : %.2f\n", getAvg(tabHeader, TABSIZE));

			printf("MinData : %.2f\n", getMin(tabData, TABSIZE));
			printf("MaxData : %.2f\n", getMax(tabData, TABSIZE));
			printf("AvgData : %.2f\n", getAvg(tabData, TABSIZE));

			printf("MinOthers : %.2f\n", getMin(tabOthers, TABSIZE));
			printf("MaxOthers : %.2f\n", getMax(tabOthers, TABSIZE));
			printf("AvgOthers : %.2f\n", getAvg(tabOthers, TABSIZE));

			printf("Total time  %.3f\n", totalTime);

			printf("Calculated fps : %.2f\n", (double) TABSIZE/totalTime);

			printf("Close time : %.2f\n", closeT);

			printAnomaly(tabStart, TABSIZE);


			if (error == NULL)
				/* Stop the acquisition */
				arv_camera_stop_acquisition (camera, &error);

			/* Destroy the stream object */
			g_clear_object (&stream);
		}

		/* Destroy the camera instance */
		g_clear_object (&camera);
	}
        

	if (error != NULL) {
		/* En error happened, display the correspdonding message */
		printf ("Error: %s\n", error->message);
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}

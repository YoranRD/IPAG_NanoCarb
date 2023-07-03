/* SPDX-License-Identifier:Unlicense */

/* Aravis header */

#include <arv.h>

/* Standard headers */

#include <stdlib.h>
#include <stdio.h>
#include <time.h>



double
getMin(double * tab, int size)
{
	double min;
	if (tab[0] > 0)
		min = tab[0];
	else 
		min = tab[1];
	for (int i = 0; i < size; ++i) {
		if (tab[i] < min && tab[i] > 0)
			min = tab[i];
	}

	return min;
}

double
getMax(double * tab, int size)
{
	double max = tab[0];
	for (int i = 0; i < size; ++i) {
		if (tab[i] > max)
			max = tab[i];
	}

	return max;
}

double
getAvg(double * tab, int size)
{
	double sum = 0;
	for (int i = 0; i < size; ++i) {
		if (tab[i] < 0)
			tab[i] = tab[i-1];
		sum += tab[i];
	}
	return sum/size;
}

void
printFirst100(double * tab, int size)
{
	for (int i = 0; i < 100; ++i) {
		printf("Tab[%d]: %f - ", i, tab[i]);
	}
	printf("\n");
}
/*
 * Connect to the first available camera, then acquire 10 buffers.
 */

int
main (int argc, char **argv)
{
	ArvCamera *camera;
	GError *error = NULL;
	ArvDevice *device;

	int TABSIZE = 1000;

	double tabStart[TABSIZE];

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
		arv_device_set_float_feature_value(device, "FrameRate", 60.0, &error);

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

			struct timespec begin, end, start, stop;
            

			if (error == NULL) {
				int img_id = 1; 
                char fileName[50];
				FILE * file  ;
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

						/* Get Timestamp and write it */
						struct timespec now;
						timespec_get(&now, TIME_UTC);											
						
						sprintf(fileName, "video/test_%d.raw", img_id);

						
						file = fopen(fileName, "wb");

						struct tm * time = gmtime(&now.tv_sec);

						int year = time->tm_year+1900;
						int month = time->tm_mon+1;
						int day = time->tm_mday;
						int hour = time->tm_hour;
						int min = time->tm_min;
						int sec = time->tm_sec;
						int msec = now.tv_nsec/1.0e6;

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
						

						/* Skip T_front, T_stirling */
						fseek(file, 16, SEEK_END);

						/* Write Data */
						fwrite(data, size, 1, file);
						++img_id;

						fclose(file);

						/* Don't destroy the buffer, but put it back into the buffer pool */
						arv_stream_push_buffer (stream, buffer);	
					}
					timespec_get(&stop, TIME_UTC);
					tabStart[i] = stop.tv_nsec/1.0e6-start.tv_nsec/1.0e6;
				}
			}

			timespec_get(&end, TIME_UTC);
			int totalTimeS = (int) end.tv_sec-begin.tv_sec;
			double totalTimeMs = (double)  (end.tv_nsec-begin.tv_nsec)/1.0e9;
			double totalTime = totalTimeS+totalTimeMs;


			printf("MinS : %.2f\n", getMin(tabStart, TABSIZE));
			printf("MaxS : %.2f\n", getMax(tabStart, TABSIZE));
			printf("AvgS : %.2f\n", getAvg(tabStart, TABSIZE));

			printf("Total time  %.3f\n", totalTime);

			printf("Calculated fps : %.2f\n", (double) TABSIZE/totalTime);


			if (error == NULL)
				/* Stop the acquisition */
				arv_camera_stop_acquisition (camera, &error);

			/* Destroy the stream object */
			g_clear_object (&stream);
		}

		/* Destroy the camera instance */
		g_clear_object (&camera);
	}

		
	/* Différence entre pop_buffer n et pop_buffer_n+1 */
	/*
	double tabDiff[TABSIZE-1];
	for (int i = 0; i < TABSIZE-1; ++i) {
		tabDiff[i] = (double) tabStart[i+1]/1.0e6-tabStart[i]/1.0e6;
	}

	printFirst100(tabDiff, TABSIZE-1);

	printf("TDiff: Min : %f\n", getMin(tabDiff, TABSIZE-1));
	printf("TDiff: Max : %f\n", getMax(tabDiff, TABSIZE-1));
	printf("TDiff: Avg : %f\n", getAvg(tabDiff, TABSIZE-1));
	*/
        

	if (error != NULL) {
		/* En error happened, display the correspdonding message */
		printf ("Error: %s\n", error->message);
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}


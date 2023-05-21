#include "lenet.h"
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#define FILE_TRAIN_IMAGE		"train-images-idx3-ubyte"
#define FILE_TRAIN_LABEL		"train-labels-idx1-ubyte"
#define FILE_TEST_IMAGE		"t10k-images-idx3-ubyte"
#define FILE_TEST_LABEL		"t10k-labels-idx1-ubyte"
#define LENET_FILE 		"model.dat"
#define COUNT_TRAIN		60000
#define COUNT_TEST		10000

// this doesn't make sense since i changed image dimensions without changing data reading
// but it doesn't matter for the sake of the challenge; it just makes the digit recognition not actually work
int read_data(unsigned char(*data)[25][25], unsigned char label[], const int count, const char data_file[], const char label_file[])
{
    FILE *fp_image = fopen(data_file, "rb");
    FILE *fp_label = fopen(label_file, "rb");
    if (!fp_image||!fp_label) return 1;
	fseek(fp_image, 16, SEEK_SET);
	fseek(fp_label, 8, SEEK_SET);
	fread(data, sizeof(*data)*count, 1, fp_image);
	fread(label,count, 1, fp_label);
	fclose(fp_image);
	fclose(fp_label);
	return 0;
}

int read_image_data(unsigned char(*data)[25][25], const char data_file[]) {
	FILE *fp_image = fopen(data_file, "rb");
	if (!fp_image) return 1;
	fseek(fp_image, 0, SEEK_SET);
	fread(data, sizeof(*data), 1, fp_image);
	fclose(fp_image);
	return 0;
}

void training(LeNet5 *lenet, image *train_data, uint8 *train_label, int batch_size, int total_size)
{
	for (int i = 0, percent = 0; i <= total_size - batch_size; i += batch_size)
	{
		TrainBatch(lenet, train_data + i, train_label + i, batch_size);
		if (i * 100 / total_size > percent)
			printf("batchsize:%d\ttrain:%2d%%\n", batch_size, percent = i * 100 / total_size);
	}
}

int testing(LeNet5 *lenet, image *test_data, uint8 *test_label,int total_size)
{
	int right = 0, percent = 0;
	for (int i = 0; i < total_size; ++i)
	{
		uint8 l = test_label[i];
		int p = Predict(lenet, test_data[i], 10);
		right += l == p;
		if (i * 100 / total_size > percent)
			printf("test:%2d%%\n", percent = i * 100 / total_size);
	}
	return right;
}

int save(LeNet5 *lenet, char filename[])
{
	FILE *fp = fopen(filename, "wb");
	if (!fp) return 1;
	fwrite(lenet, sizeof(LeNet5), 1, fp);
	fclose(fp);
	return 0;
}

int load(LeNet5 *lenet, char filename[])
{
	FILE *fp = fopen(filename, "rb");
	if (!fp) return 1;
	fread(lenet, sizeof(LeNet5), 1, fp);
	fclose(fp);
	return 0;
}

void foo()
{
	LeNet5 *lenet = (LeNet5 *)malloc(sizeof(LeNet5));
	if (load(lenet, LENET_FILE))
		Initial(lenet);


	image* flag = (image *)calloc(1, sizeof(image));
	if (read_image_data(flag, "flag.data"))
	{
		printf("error file not found\n");
		free(flag);
	}
	LeNet5 grad = Gradient(lenet, *flag, 6);
	save(&grad, "grad.dat");

	free(lenet);
	free(flag);
}

int main()
{
	foo();
	return 0;
}
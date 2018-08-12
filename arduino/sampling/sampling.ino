#define METRICS_OUTPUT 0

#define MIC_L A0 // left microphone
#define MIC_R A1 // right microphone

#define BATCH_SIZE 800

#define SERIAL_SPEED 57600

#define START_SIGNAL 'S'
#define END_SIGNAL 'E'

#define MSEC_TO_SEC(msec) (msec/1000000)

#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))

byte left_sensor_value[BATCH_SIZE];
byte right_sensor_value[BATCH_SIZE];

void setup() {
  sbi(ADCSRA, ADPS2); sbi(ADCSRA, ADPS1); cbi(ADCSRA, ADPS0); // 9kHz sampling
  //sbi(ADCSRA, ADPS2); cbi(ADCSRA, ADPS1); sbi(ADCSRA, ADPS0); // 17kHz sampling
  //sbi(ADCSRA, ADPS2); cbi(ADCSRA, ADPS1); cbi(ADCSRA, ADPS0); // 32kHz sampling

  Serial.begin(SERIAL_SPEED);
}

void loop() {

#if METRICS_OUTPUT
  long t0, t1, t2;

  t0 = micros();
#endif

  // Sample batch
  for(int i = 0; i < BATCH_SIZE; i++){
    left_sensor_value[i] = (byte)(1024 - analogRead(MIC_L));
    right_sensor_value[i] = (byte)(1024 - analogRead(MIC_R));
  }
  
#if METRICS_OUTPUT
  t1 = micros() - t0;
#endif
  
  // Start sending batch samples

  Serial.write(START_SIGNAL);
  Serial.write((byte)(BATCH_SIZE >> 8)); Serial.write((byte)BATCH_SIZE); // Send batch size (int16)
  
  for(int i = 0; i < BATCH_SIZE; i++){
    Serial.write(left_sensor_value[i]);
    Serial.write(right_sensor_value[i]);
  }

  Serial.write(END_SIGNAL);

#if METRICS_OUTPUT
  t2 = micros() - t0;


  Serial.print("Time per ");
  Serial.print(BATCH_SIZE);
  Serial.print(" samples (without transmission): ");
  Serial.print(MSEC_TO_SEC((float)t1));
  Serial.println();
  
  Serial.print("Sampling frequency:");
  Serial.print(BATCH_SIZE/MSEC_TO_SEC((float)t1));
  Serial.println();

  Serial.print("Time per ");
  Serial.print(BATCH_SIZE);
  Serial.print(" samples (with transmission): ");
  Serial.print(MSEC_TO_SEC((float)t2));
  Serial.println();

  Serial.print("Sampling frequency (with transmission):");
  Serial.print(BATCH_SIZE/MSEC_TO_SEC((float)t2));
  Serial.println();
  
  delay(2000);
#endif
}

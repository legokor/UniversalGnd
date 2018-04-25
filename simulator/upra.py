import time
import socket
import threading

DATA = ['$$HAxUPRA,002,336677,+9500.000,+18888.000,41110,0170,006,002,',
        '$$HAxUPRA,002,336677,+9500.000,+18888.000,41110,0170,006,002,',
        '$$HAxUPRA,003,073640,+4728.407,+01903.673,00103,0181,008,001,',
        '$$HAxUPRA,003,073640,+4728.407,+01903.673,00103,0181,008,001,',
        '$$HAxUPRA,004,073647,+4728.407,+01903.673,00104,0173,-01,001,',
        '$$HAxUPRA,004,073647,+4728.407,+01903.673,00104,0173,-01,001,',
        '$$HAxUPRA,005,073654,+4728.407,+01903.673,00105,0174,005,002,',
        '$$HAxUPRA,005,073654,+4728.407,+01903.673,00105,0174,005,002,',
        '$$HAxUPRA,006,073701,+4728.407,+01903.673,00106,0169,020,008,',
        '$$HAxUPRA,006,073701,+4728.407,+01903.673,00106,0169,020,008,',
        '$$HAxUPRA,007,073708,+4728.408,+01903.673,00107,0180,001,002,',
        '$$HAxUPRA,007,073708,+4728.408,+01903.673,00107,0180,001,002,',
        '$$HAxUPRA,009,073728,+4728.406,+01903.674,00106,0173,005,002,',
        '$$HAxUPRA,009,073728,+4728.406,+01903.674,00106,0173,005,002,',
        '$$HAxUPRA,010,073738,+4728.406,+01903.673,00106,0169,002,001,',
        '$$HAxUPRA,010,073738,+4728.406,+01903.673,00106,0169,002,001,',
        '$$HAxUPRA,011,073748,+4728.406,+01903.673,00108,0170,004,001,',
        '$$HAxUPRA,011,073748,+4728.406,+01903.673,00108,0170,004,001,',
        '$$HAxUPRA,000,336677,+9500.000,+18888.000,41110,0218,003,000,',
        '$$HAxUPRA,001,336677,+9500.000,+18888.000,41110,0204,009,004,',
        '$$HAxUPRA,002,336677,+9500.000,+18888.000,41110,0211,004,-00,',
        '$$HAxUPRA,002,336677,+9500.000,+18888.000,41110,0211,004,-00,',
        '$$HAxUPRA,003,336677,+9500.000,+18888.000,41110,0187,-03,002,',
        '$$HAxUPRA,003,336677,+9500.000,+18888.000,41110,0187,-03,002,',
        '$$HAxUPRA,004,336677,+9500.000,+18888.000,41110,0196,-02,001,',
        '$$HAxUPRA,004,336677,+9500.000,+18888.000,41110,0196,-02,001,',
        '$$HAxUPRA,005,082346,+4728.413,+01903.523,00015,0197,007,003,',
        '$$HAxUPRA,005,082346,+4728.413,+01903.523,00015,0197,007,003,',
        '$$HAxUPRA,006,082353,+4728.414,+01903.522,00011,0192,008,002,',
        '$$HAxUPRA,006,082353,+4728.414,+01903.522,00011,0192,008,002,',
        '$$HAxUPRA,007,082353,+4728.414,+01903.522,00011,0193,004,003,',
        '$$HAxUPRA,007,082353,+4728.414,+01903.522,00011,0193,004,003,',
        '$$HAxUPRA,008,082413,+4728.424,+01903.460,00000,0205,003,001,',
        '$$HAxUPRA,008,082413,+4728.424,+01903.460,00000,0205,003,001,',
        '$$HAxUPRA,010,082433,+4728.422,+01903.554,00053,0207,000,000,',
        '$$HAxUPRA,010,082433,+4728.422,+01903.554,00053,0207,000,000,',
        '$$HAxUPRA,011,082443,+4728.429,+01903.565,00070,0193,004,-00,',
        '$$HAxUPRA,011,082443,+4728.429,+01903.565,00070,0193,004,-00,',
        '$$HAxUPRA,012,082453,+4728.445,+01903.569,00071,0191,-00,012,',
        '$$HAxUPRA,012,082453,+4728.445,+01903.569,00071,0191,-00,012,',
        '$$HAxUPRA,013,082503,+4728.439,+01903.489,00000,0197,008,000,',
        '$$HAxUPRA,013,082503,+4728.439,+01903.489,00000,0197,008,000,',
        '$$HAxUPRA,014,082513,+4728.432,+01903.511,00019,0204,-00,001,',
        '$$HAxUPRA,014,082513,+4728.432,+01903.511,00019,0204,-00,001,',
        '$$HAxUPRA,015,082523,+4728.425,+01903.533,00032,0187,003,003,',
        '$$HAxUPRA,016,082533,+4728.415,+01903.640,00123,0193,009,003,',
        '$$HAxUPRA,016,082533,+4728.415,+01903.640,00123,0193,009,003,',
        '$$HAxUPRA,017,082543,+4728.420,+01903.642,00127,0195,000,002,',
        '$$HAxUPRA,018,082553,+4728.418,+01903.644,00132,0200,002,000,',
        '$$HAxUPRA,019,082603,+4728.419,+01903.644,00132,0203,009,004,',
        '$$HAxUPRA,019,082603,+4728.419,+01903.644,00132,0203,009,004,',
        '$$HAxUPRA,020,082613,+4728.419,+01903.643,00134,0190,009,001,',
        '$$HAxUPRA,020,082613,+4728.419,+01903.643,00134,0190,009,001,',
        '$$HAxUPRA,021,082623,+4728.422,+01903.640,00131,0203,007,002,',
        '$$HAxUPRA,021,082623,+4728.422,+01903.640,00131,0203,007,002,',
        '$$HAxUPRA,022,082633,+4728.413,+01903.649,00131,0327,002,001,',
        '$$HAxUPRA,022,082633,+4728.413,+01903.649,00131,0327,002,001,',
        '$$HAxUPRA,023,082643,+4728.420,+01903.649,00202,0326,004,000,',
        '$$HAxUPRA,023,082643,+4728.420,+01903.649,00202,0326,004,000,',
        '$$HAxUPRA,024,082653,+4728.435,+01903.645,00276,0244,-01,001,',
        '$$HAxUPRA,024,082653,+4728.435,+01903.645,00276,0244,-01,001,',
        '$$HAxUPRA,025,082703,+4728.455,+01903.635,00330,0313,006,000,',
        '$$HAxUPRA,025,082703,+4728.455,+01903.635,00330,0313,006,000,',
        '$$HAxUPRA,026,082713,+4728.478,+01903.632,00386,0262,005,001,',
        '$$HAxUPRA,026,082713,+4728.478,+01903.632,00386,0262,005,001,',
        '$$HAxUPRA,027,082723,+4728.509,+01903.630,00445,0291,001,001,',
        '$$HAxUPRA,027,082723,+4728.509,+01903.630,00445,0291,001,001,',
        '$$HAxUPRA,028,082733,+4728.545,+01903.639,00514,0240,004,000,',
        '$$HAxUPRA,028,082733,+4728.545,+01903.639,00514,0240,004,000,',
        '$$HAxUPRA,029,082753,+4728.634,+01903.648,00653,0242,000,000,',
        '$$HAxUPRA,029,082753,+4728.634,+01903.648,00653,0242,000,000,',
        '$$HAxUPRA,030,082810,+4728.724,+01903.689,00772,0238,003,003,',
        '$$HAxUPRA,030,082810,+4728.724,+01903.689,00772,0238,003,003,',
        '$$HAxUPRA,031,082827,+4728.825,+01903.737,00886,0215,003,002,',
        '$$HAxUPRA,031,082827,+4728.825,+01903.737,00886,0215,003,002,',
        '$$HAxUPRA,032,082844,+4728.935,+01903.813,01000,0216,005,003,',
        '$$HAxUPRA,032,082844,+4728.935,+01903.813,01000,0216,005,003,',
        '$$HAxUPRA,033,082901,+4729.049,+01903.907,01106,0153,024,009,',
        '$$HAxUPRA,033,082901,+4729.049,+01903.907,01106,0153,024,009,',
        '$$HAxUPRA,034,082918,+4729.164,+01904.010,01214,0160,003,002,',
        '$$HAxUPRA,034,082918,+4729.164,+01904.010,01214,0160,003,002,',
        '$$HAxUPRA,035,082935,+4729.282,+01904.158,01332,0177,002,-00,',
        '$$HAxUPRA,035,082935,+4729.282,+01904.158,01332,0177,002,-00,',
        '$$HAxUPRA,036,082952,+4729.392,+01904.300,01439,0135,002,000,',
        '$$HAxUPRA,036,082952,+4729.392,+01904.300,01439,0135,002,000,',
        '$$HAxUPRA,037,083009,+4729.499,+01904.437,01554,0134,004,002,',
        '$$HAxUPRA,037,083009,+4729.499,+01904.437,01554,0134,004,002,',
        '$$HAxUPRA,038,083026,+4729.617,+01904.595,01667,0138,002,002,',
        '$$HAxUPRA,038,083026,+4729.617,+01904.595,01667,0138,002,002,',
        '$$HAxUPRA,039,083043,+4729.726,+01904.773,01778,0112,011,001,',
        '$$HAxUPRA,039,083043,+4729.726,+01904.773,01778,0112,011,001,',
        '$$HAxUPRA,040,083100,+4729.842,+01904.945,01887,0102,003,009,',
        '$$HAxUPRA,040,083100,+4729.842,+01904.945,01887,0102,003,009,',
        '$$HAxUPRA,041,083117,+4729.960,+01905.135,02001,0100,004,003,',
        '$$HAxUPRA,041,083117,+4729.960,+01905.135,02001,0100,004,003,',
        '$$HAxUPRA,042,083134,+4730.079,+01905.321,02112,0098,004,000,',
        '$$HAxUPRA,042,083134,+4730.079,+01905.321,02112,0098,004,000,',
        '$$HAxUPRA,043,083151,+4730.191,+01905.493,02225,0086,-02,002,',
        '$$HAxUPRA,043,083151,+4730.191,+01905.493,02225,0086,-02,002,',
        '$$HAxUPRA,044,083208,+4730.302,+01905.670,02344,0075,005,-01,',
        '$$HAxUPRA,044,083208,+4730.302,+01905.670,02344,0075,005,-01,',
        '$$HAxUPRA,045,083225,+4730.395,+01905.858,02465,0054,004,001,',
        '$$HAxUPRA,045,083225,+4730.395,+01905.858,02465,0054,004,001,',
        '$$HAxUPRA,046,083242,+4730.503,+01906.053,02583,0057,006,001,',
        '$$HAxUPRA,046,083242,+4730.503,+01906.053,02583,0057,006,001,',
        '$$HAxUPRA,047,083259,+4730.601,+01906.230,02709,0079,001,008,',
        '$$HAxUPRA,047,083259,+4730.601,+01906.230,02709,0079,001,008,',
        '$$HAxUPRA,048,083316,+4730.711,+01906.393,02840,0064,006,001,',
        '$$HAxUPRA,048,083316,+4730.711,+01906.393,02840,0064,006,001,',
        '$$HAxUPRA,049,083333,+4730.803,+01906.571,02976,0075,-03,002,',
        '$$HAxUPRA,049,083333,+4730.803,+01906.571,02976,0075,-03,002,',
        '$$HAxUPRA,050,083350,+4730.907,+01906.770,03111,0047,001,003,',
        '$$HAxUPRA,050,083350,+4730.907,+01906.770,03111,0047,001,003,',
        '$$HAxUPRA,051,083407,+4731.006,+01906.992,03239,0043,007,000,',
        '$$HAxUPRA,051,083407,+4731.006,+01906.992,03239,0043,007,000,',
        '$$HAxUPRA,052,083424,+4731.102,+01907.209,03374,0030,-02,003,',
        '$$HAxUPRA,052,083424,+4731.102,+01907.209,03374,0030,-02,003,',
        '$$HAxUPRA,054,083458,+4731.296,+01907.640,03637,0016,001,001,',
        '$$HAxUPRA,054,083458,+4731.296,+01907.640,03637,0016,001,001,',
        '$$HAxUPRA,055,083515,+4731.386,+01907.840,03772,0002,-02,002,',
        '$$HAxUPRA,055,083515,+4731.386,+01907.840,03772,0002,-02,002,',
        '$$HAxUPRA,056,083532,+4731.474,+01908.038,03902,0001,001,-01,',
        '$$HAxUPRA,056,083532,+4731.474,+01908.038,03902,0001,001,-01,',
        '$$HAxUPRA,057,083549,+4731.561,+01908.233,04027,0009,000,000,',
        '$$HAxUPRA,057,083549,+4731.561,+01908.233,04027,0009,000,000,',
        '$$HAxUPRA,059,083623,+4731.746,+01908.675,04276,-009,002,000,',
        '$$HAxUPRA,059,083623,+4731.746,+01908.675,04276,-009,002,000,',
        '$$HAxUPRA,060,083640,+4731.823,+01908.880,04400,-033,002,-00,',
        '$$HAxUPRA,060,083640,+4731.823,+01908.880,04400,-033,002,-00,',
        '$$HAxUPRA,061,083657,+4731.918,+01909.084,04538,-033,-03,004,',
        '$$HAxUPRA,062,083714,+4732.019,+01909.262,04670,-015,003,003,',
        '$$HAxUPRA,062,083714,+4732.019,+01909.262,04670,-015,003,003,',
        '$$HAxUPRA,063,083731,+4732.140,+01909.480,04798,-040,-01,-01,',
        '$$HAxUPRA,064,083748,+4732.274,+01909.682,04928,-057,001,001,',
        '$$HAxUPRA,064,083748,+4732.274,+01909.682,04928,-057,001,001,',
        '$$HAxUPRA,065,083805,+4732.393,+01909.899,05053,-079,002,002,',
        '$$HAxUPRA,065,083805,+4732.393,+01909.899,05053,-079,002,002,',
        '$$HAxUPRA,066,083822,+4732.510,+01910.128,05182,-080,000,001,',
        '$$HAxUPRA,066,083822,+4732.510,+01910.128,05182,-080,000,001,',
        '$$HAxUPRA,067,083837,+4732.639,+01910.349,05313,-098,-03,002,',
        '$$HAxUPRA,067,083837,+4732.639,+01910.349,05313,-098,-03,002,',
        '$$HAxUPRA,068,083854,+4732.775,+01910.582,05437,-097,000,000,',
        '$$HAxUPRA,069,083911,+4732.921,+01910.822,05567,-107,-02,001,',
        '$$HAxUPRA,069,083911,+4732.921,+01910.822,05567,-107,-02,001,',
        '$$HAxUPRA,070,083928,+4733.106,+01911.087,05709,-092,004,002,',
        '$$HAxUPRA,071,083945,+4733.306,+01911.352,05860,-099,001,000,',
        '$$HAxUPRA,071,083945,+4733.306,+01911.352,05860,-099,001,000,',
        '$$HAxUPRA,072,084002,+4733.520,+01911.633,06002,1644,017,001,',
        '$$HAxUPRA,072,084002,+4733.520,+01911.633,06002,1644,017,001,',
        '$$HAxUPRA,073,084019,+4733.707,+01911.890,06133,-118,000,001,',
        '$$HAxUPRA,073,084019,+4733.707,+01911.890,06133,-118,000,001,',
        '$$HAxUPRA,074,084036,+4733.919,+01912.148,06256,-119,005,001,',
        '$$HAxUPRA,075,084053,+4734.114,+01912.419,06398,-135,001,001,',
        '$$HAxUPRA,075,084053,+4734.114,+01912.419,06398,-135,001,001,',
        '$$HAxUPRA,076,084110,+4734.350,+01912.694,06529,-129,006,000,',
        '$$HAxUPRA,077,084127,+4734.604,+01912.978,06661,-146,000,001,',
        '$$HAxUPRA,077,084127,+4734.604,+01912.978,06661,-146,000,001,',
        '$$HAxUPRA,078,084144,+4734.879,+01913.277,06784,-125,006,000,',
        '$$HAxUPRA,078,084144,+4734.879,+01913.277,06784,-125,006,000,',
        '$$HAxUPRA,079,084201,+4735.166,+01913.572,06926,-131,018,006,',
        '$$HAxUPRA,079,084201,+4735.166,+01913.572,06926,-131,018,006,',
        '$$HAxUPRA,080,084218,+4735.440,+01913.853,07054,-143,004,-00,',
        '$$HAxUPRA,080,084218,+4735.440,+01913.853,07054,-143,004,-00,',
        '$$HAxUPRA,081,084235,+4735.718,+01914.130,07176,-187,-02,001,',
        '$$HAxUPRA,081,084235,+4735.718,+01914.130,07176,-187,-02,001,',
        '$$HAxUPRA,082,084252,+4736.012,+01914.427,07313,-190,005,003,',
        '$$HAxUPRA,082,084252,+4736.012,+01914.427,07313,-190,005,003,',
        '$$HAxUPRA,083,084309,+4736.299,+01914.701,07437,-198,-05,001,',
        '$$HAxUPRA,083,084309,+4736.299,+01914.701,07437,-198,-05,001,',
        '$$HAxUPRA,084,084326,+4736.587,+01914.983,07573,-183,000,000,',
        '$$HAxUPRA,085,084343,+4736.869,+01915.283,07700,-202,002,002,',
        '$$HAxUPRA,085,084343,+4736.869,+01915.283,07700,-202,002,002,',
        '$$HAxUPRA,086,084400,+4737.153,+01915.568,07836,-209,004,006,',
        '$$HAxUPRA,087,084417,+4737.434,+01915.852,07959,-207,000,000,',
        '$$HAxUPRA,087,084417,+4737.434,+01915.852,07959,-207,000,000,',
        '$$HAxUPRA,088,084434,+4737.712,+01916.151,08087,-233,008,-01,',
        '$$HAxUPRA,088,084434,+4737.712,+01916.151,08087,-233,008,-01,',
        '$$HAxUPRA,089,084451,+4737.993,+01916.472,08230,-253,-04,002,',
        '$$HAxUPRA,089,084451,+4737.993,+01916.472,08230,-253,-04,002,',
        '$$HAxUPRA,090,084508,+4738.269,+01916.802,08354,-255,006,001,',
        '$$HAxUPRA,091,084525,+4738.535,+01917.114,08486,-246,-02,-01,',
        '$$HAxUPRA,091,084525,+4738.535,+01917.114,08486,-246,-02,-01,',
        '$$HAxUPRA,092,084542,+4738.798,+01917.436,08613,-259,-06,-01,',
        '$$HAxUPRA,095,084633,+4739.564,+01918.461,08989,-300,006,000,',
        '$$HAxUPRA,098,084724,+4740.170,+01919.589,09334,-326,-07,-01,',
        ]


def listen():
    while running:
        connection, address = sck.accept()
        print('client connected')
        thread = threading.Thread(target=digest_message, args=(connection,))
        thread.daemon = True
        thread.start()


def digest_message(conn):
    while running:
        digest = conn.recv(1)
        print(digest)
        if digest == b'o':
            print('sending')
            for entry in DATA:
                conn.send(bytes(entry, 'UTF-8'))
                time.sleep(0.2)


running = True

sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck.bind(('0.0.0.0', 1337))
sck.listen(5)

t1 = threading.Thread(target=listen)
t1.daemon = True
t1.start()

while running:
    cmd = input('? ')
    if cmd == "exit":
        running = False

import io
import librosa

from transformers import AutoProcessor, TFAutoModelForSpeechSeq2Seq, logging
from typing import TYPE_CHECKING

from besser.bot.nlp.speech2text.speech2text import Speech2Text

from src.utils.session_state_keys import NLP_LANGUAGE, NLP_STT_HF_MODEL

if TYPE_CHECKING:
    from src.app.app import App

logging.set_verbosity_error()


class Speech2Text(Speech2Text):
    """A Hugging Face Speech2Text.

    It loads a Speech2Text Hugging Face model to perform the Speech2Text task.

    Args:
        app (App): the App where the Speech2Text component is running

    Attributes:
        _model_name (str): the Hugging Face model name
        _processor (): the model text processor
        _model (): the Speech2Text model
        _sampling_rate (int): the sampling rate of audio data, it must coincide with the sampling rate used to train the
            model
        _forced_decoder_ids (list): the decoder ids
    """

    def __init__(self, app: 'App'):
        self.app: 'App' = app
        self._model_name: str = self.app.properties[NLP_STT_HF_MODEL]
        self._processor = AutoProcessor.from_pretrained(self._model_name)
        self._model = TFAutoModelForSpeechSeq2Seq.from_pretrained(self._model_name)
        self._sampling_rate: int = 16000
        # self.model.config.forced_decoder_ids = None
        self._forced_decoder_ids = self._processor.get_decoder_prompt_ids(
            language=self.app.properties[NLP_LANGUAGE], task="transcribe"
        )

    def speech2text(self, speech: bytes):
        wav_stream = io.BytesIO(speech)
        audio, sampling_rate = librosa.load(wav_stream, sr=self._sampling_rate)
        input_features = self._processor(audio, sampling_rate=self._sampling_rate, return_tensors="tf").input_features
        predicted_ids = self._model.generate(input_features, forced_decoder_ids=self._forced_decoder_ids)
        transcriptions = self._processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return transcriptions[0]

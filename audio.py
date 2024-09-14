import PyPDF2
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from gtts import gTTS
import os


device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load LLaMA model and tokenizer with automatic device placement for large models
def load_llama_model():
    model_name = "meta-llama/Llama-2-7b-chat-hf"  
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",  
        torch_dtype=torch.float16  
    ).to(device)
    return model, tokenizer

def pdf_to_text(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def split_text(text, chunk_size=1000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def process_text_with_llama(text_chunk, model, tokenizer):
    inputs = tokenizer(f"Summarize and explain this text for a natural audiobook narration:\n\n{text_chunk}", return_tensors='pt')
    inputs = {key: value.to(device) for key, value in inputs.items()}
    outputs = model.generate(inputs['input_ids'], max_length=500)
    processed_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return processed_text

def text_to_speech(text, output_file):
    """Convert the LLM-processed text to speech."""
    tts = gTTS(text, lang='en-in')
    tts.save(output_file)

def convert_pdf_to_audiobook(pdf_file, output_audio_file):    
    # Load LLaMA model and tokenizer
    model, tokenizer = load_llama_model()
    raw_text = pdf_to_text(pdf_file)
    text_chunks = split_text(raw_text)
    
    full_audio_text = ""
    
    # Process each text chunk using LLaMA and concatenate the output
    for i, chunk in enumerate(text_chunks):
        print(f"Processing chunk {i + 1} of {len(text_chunks)}")
        processed_text = process_text_with_llama(chunk, model, tokenizer)
        full_audio_text += processed_text + " "  # Concatenate all the processed text
    
    # Convert the concatenated processed text to a single audio file
    text_to_speech(full_audio_text, output_audio_file)
    print(f"All chunks processed. Full audiobook saved as {output_audio_file}")

if __name__ == "__main__":
    pdf_file_path = 'file_name.pdf'  # Specify your PDF file here
    output_audio_file = 'audiobook.mp3'  # Specify the name of the single output audio file

    convert_pdf_to_audiobook(pdf_file_path, output_audio_file)

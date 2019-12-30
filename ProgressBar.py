import sys

class ProgressBar:
    def __init__(self, title: str, max_score: int, steps: int = 10, progress_length: int = 4) -> None:
        '''
        Initializer for the ProgressBar. Sets the given title, and max_score, and initializes
        current_progess as zero.
        steps equals the number of times the progress bar is updated.
        progress_length equals the number of times '#' is printed when show_progress is called.
        '''
        self.title = title
        self.max_score = max_score
        self.current_progress = 0
        self.step_size = max_score/steps
        self.progress_length = progress_length

    def start_progress(self) -> None:
        '''
        prints the title on the screen, to mark the start of progress bar.
        '''
        sys.stdout.write(self.title + ": [")
        sys.stdout.flush()

    def update_progress(self, current_score: int) -> None:
        '''
        updates the progress bar with the current_score.
        '''
        if current_score % self.step_size == 0:
            self.show_progress()

    def show_progress(self) -> None:
        '''
        adds '#' to the progress bar. Progress_length equals the number of times '#' is added.
        '''
        self.current_progress += self.progress_length
        sys.stdout.write("#" * (self.progress_length))
        sys.stdout.flush()

    def end_progress(self) -> None:
        '''
        ends the progress bar after printing any necesarry details.
        '''
        sys.stdout.write("#" * int((self.progress_length*(self.max_score/self.step_size))  - self.current_progress) + "]\n")
        sys.stdout.flush()